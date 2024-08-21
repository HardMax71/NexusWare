# /server/app/api/v1/endpoints/notifications.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from public_api.shared_schemas import Notification, NotificationCreate, NotificationUpdate
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.get("/", response_model=List[Notification])
def get_notifications(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.notification.get_user_notifications(db, current_user.id, skip, limit)


@router.post("/", response_model=Notification)
def create_notification(
        notification: NotificationCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.notification.create(db, obj_in=notification)


@router.put("/read-all", response_model=List[Notification])
def mark_all_notifications_as_read(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.notification.mark_all_as_read(db, current_user.id)

@router.get("/unread", response_model=List[Notification])
def get_unread_notifications(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.notification.get_user_unread_notifications(db, current_user.id, skip, limit)


@router.put("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(
        notification_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    notification = crud.notification.mark_notification_as_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.get("/{notification_id}", response_model=Notification)
def get_notification(
        notification_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    notification = crud.notification.get(db, id=notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.put("/{notification_id}", response_model=Notification)
def update_notification(
        notification_id: int,
        notification_update: NotificationUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    notification = crud.notification.get(db, id=notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return crud.notification.update(db, db_obj=notification, obj_in=notification_update)


@router.delete("/{notification_id}", response_model=Notification)
def delete_notification(
        notification_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    notification = crud.notification.get(db, id=notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return crud.notification.remove(db, id=notification_id)
