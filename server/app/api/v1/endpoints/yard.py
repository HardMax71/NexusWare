# /server/app/api/v1/endpoints/yard.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


# Yard Location routes
@router.post("/locations", response_model=schemas.YardLocation)
def create_yard_location(
        location: schemas.YardLocationCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.yard_location.create(db=db, obj_in=location)


@router.get("/locations", response_model=List[schemas.YardLocation])
def read_yard_locations(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.YardLocationFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.yard_location.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/locations/{location_id}", response_model=schemas.YardLocationWithAppointments)
def read_yard_location(
        location_id: int = Path(..., title="The ID of the yard location to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.yard_location.get_with_appointments(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Yard location not found")
    return location


@router.put("/locations/{location_id}", response_model=schemas.YardLocation)
def update_yard_location(
        location_id: int = Path(..., title="The ID of the yard location to update"),
        location_in: schemas.YardLocationUpdate = Body(..., title="Yard location update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.yard_location.get(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Yard location not found")
    return crud.yard_location.update(db, db_obj=location, obj_in=location_in)


@router.delete("/locations/{location_id}", response_model=schemas.YardLocation)
def delete_yard_location(
        location_id: int = Path(..., title="The ID of the yard location to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    location = crud.yard_location.get(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Yard location not found")
    return crud.yard_location.remove(db, id=location_id)


# Dock Appointment routes
@router.post("/appointments", response_model=schemas.DockAppointment)
def create_dock_appointment(
        appointment: schemas.DockAppointmentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    conflicts = crud.dock_appointment.check_conflicts(db, appointment)
    if conflicts:
        raise HTTPException(status_code=400,
                            detail={"message": "Appointment conflicts detected", "conflicts": conflicts})
    return crud.dock_appointment.create(db=db, obj_in=appointment)


@router.get("/appointments", response_model=List[schemas.DockAppointment])
def read_dock_appointments(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.DockAppointmentFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.dock_appointment.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/appointments/{appointment_id}", response_model=schemas.DockAppointment)
def read_dock_appointment(
        appointment_id: int = Path(..., title="The ID of the dock appointment to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    appointment = crud.dock_appointment.get(db, id=appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Dock appointment not found")
    return appointment


@router.put("/appointments/{appointment_id}", response_model=schemas.DockAppointment)
def update_dock_appointment(
        appointment_id: int = Path(..., title="The ID of the dock appointment to update"),
        appointment_in: schemas.DockAppointmentUpdate = Body(..., title="Dock appointment update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    appointment = crud.dock_appointment.get(db, id=appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Dock appointment not found")
    conflicts = crud.dock_appointment.check_conflicts(db, appointment_in, exclude_id=appointment_id)
    if conflicts:
        raise HTTPException(status_code=400,
                            detail={"message": "Appointment conflicts detected", "conflicts": conflicts})
    return crud.dock_appointment.update(db, db_obj=appointment, obj_in=appointment_in)


@router.delete("/appointments/{appointment_id}", response_model=schemas.DockAppointment)
def delete_dock_appointment(
        appointment_id: int = Path(..., title="The ID of the dock appointment to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    appointment = crud.dock_appointment.get(db, id=appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Dock appointment not found")
    return crud.dock_appointment.remove(db, id=appointment_id)


# Additional yard management operations
@router.get("/stats", response_model=schemas.YardStats)
def get_yard_stats(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.yard.get_stats(db)


@router.get("/utilization", response_model=schemas.YardUtilizationReport)
def get_yard_utilization(
        date: datetime = Query(None),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.yard.get_utilization_report(db, date=date or datetime.now())


@router.get("/carrier-performance", response_model=List[schemas.CarrierPerformance])
def get_carrier_performance(
        start_date: datetime = Query(...),
        end_date: datetime = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.yard.get_carrier_performance(db, start_date=start_date, end_date=end_date)


@router.post("/check-availability", response_model=List[schemas.AppointmentConflict])
def check_appointment_availability(
        appointment: schemas.DockAppointmentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.dock_appointment.check_conflicts(db, appointment)
