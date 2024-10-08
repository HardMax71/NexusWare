from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from public_api.shared_schemas import (
    YardStats, YardUtilizationReport,
    CarrierPerformance, YardLocationCapacity
)
from app.models import YardLocation, DockAppointment, Carrier


class CRUDYard:
    def get_stats(self, db: Session) -> YardStats:
        total_locations = db.query(func.count(YardLocation.id)).scalar()
        occupied_locations = db.query(func.count(YardLocation.id)).filter(
            YardLocation.status == "occupied").scalar()
        total_appointments = db.query(func.count(DockAppointment.id)).scalar()
        upcoming_appointments = db.query(func.count(DockAppointment.id)).filter(
            DockAppointment.appointment_time > func.now(),
            DockAppointment.status == "scheduled"
        ).scalar()

        return YardStats(
            total_locations=total_locations,
            occupied_locations=occupied_locations,
            total_appointments=total_appointments,
            upcoming_appointments=upcoming_appointments
        )

    def get_utilization_report(self, db: Session, date: int) -> YardUtilizationReport:
        locations = db.query(YardLocation).all()
        total_capacity = sum(location.capacity for location in locations)
        total_utilization = db.query(func.count(DockAppointment.id)).filter(
            func.date(DockAppointment.appointment_time) == func.to_timestamp(date)
        ).scalar()

        location_breakdown = []
        for location in locations:
            occupancy = db.query(func.count(DockAppointment.id)).filter(
                DockAppointment.yard_location_id == location.yard_location_id,
                func.date(DockAppointment.appointment_time) == func.to_timestamp(date)
            ).scalar()
            location_breakdown.append(YardLocationCapacity(
                yard_location_id=location.yard_location_id,
                name=location.name,
                capacity=location.capacity,
                current_occupancy=occupancy
            ))

        return YardUtilizationReport(
            date=date,
            total_capacity=total_capacity,
            total_utilization=total_utilization,
            utilization_percentage=(total_utilization / total_capacity) * 100 if total_capacity > 0 else 0,
            location_breakdown=location_breakdown
        )

    def get_carrier_performance(self, db: Session,
                                start_date: int, end_date: int) -> List[CarrierPerformance]:
        carriers = db.query(Carrier).all()
        performance_data = []

        for carrier in carriers:
            appointments = db.query(DockAppointment).filter(
                DockAppointment.carrier_id == carrier.id,
                DockAppointment.appointment_time.between(func.to_timestamp(start_date), func.to_timestamp(end_date))
            ).all()

            total_appointments = len(appointments)
            on_time_appointments = sum(
                1 for a in appointments if a.status == "completed" and a.actual_arrival_time <= a.appointment_time)
            late_appointments = sum(
                1 for a in appointments if a.status == "completed" and a.actual_arrival_time > a.appointment_time)
            missed_appointments = sum(1 for a in appointments if a.status == "missed")

            dwell_times = [
                (a.actual_departure_time - a.actual_arrival_time).total_seconds() / 60
                for a in appointments
                if a.status == "completed" and a.actual_arrival_time and a.actual_departure_time
            ]
            average_dwell_time = sum(dwell_times) / len(dwell_times) if dwell_times else 0

            performance_data.append(CarrierPerformance(
                carrier_id=carrier.id,
                carrier_name=carrier.name,
                total_appointments=total_appointments,
                on_time_appointments=on_time_appointments,
                late_appointments=late_appointments,
                missed_appointments=missed_appointments,
                average_dwell_time=average_dwell_time
            ))

        return performance_data


yard = CRUDYard()
