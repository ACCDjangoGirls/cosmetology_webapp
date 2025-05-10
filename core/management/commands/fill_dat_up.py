#Instructions below are not written by me:

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

from core.models import Service, ServiceProfessional, Event, Reservation, Review

class Command(BaseCommand):
    help = "Populate DB with logic-enforced Services, Professionals, Events, Reservations, and Reviews"

    def handle(self, *args, **options):
        fake = Faker()
        now = timezone.now()

        # Clear existing data (except superusers)
        Review.objects.all().delete()
        Reservation.objects.all().delete()
        Event.objects.all().delete()
        ServiceProfessional.objects.all().delete()
        Service.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write("Creating demo users…")
        users = []
        for _ in range(5):
            u = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="password123"
            )
            users.append(u)

        self.stdout.write("Creating services…")
        services = []
        base_services = ["Haircut", "Manicure", "Pedicure", "Facial", "Massage"]
        for name in base_services:
            svc = Service.objects.create(
                name=name,
                service_description=fake.sentence(nb_words=6),
                price=random.randint(20, 150)
            )
            services.append(svc)

        self.stdout.write("Creating professionals…")
        pros = []
        for _ in range(4):
            pro = ServiceProfessional.objects.create(
                name=fake.name(),
                class_period=f"{random.randint(1,4)} months"
            )
            pro.services.set(random.sample(services, k=random.randint(1,3)))
            pros.append(pro)

        self.stdout.write("Creating events (some past, some future)…")
        events = []
        for _ in range(5):
            offset = random.randint(-30, 30)
            start = now + timedelta(days=offset, hours=random.randint(8,11))
            duration = timedelta(hours=random.choice([2,3,4]))
            ev = Event.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=100),
                start_time_and_date=start,
                end_time=start + duration,
                event_location=fake.city()
            )
            ev.services.set(random.sample(services, k=random.randint(2,4)))
            events.append(ev)

        self.stdout.write("Creating reservations with enforced logic…")
        created = 0
        attempts = 0
        while created < 15 and attempts < 100:
            attempts += 1
            user = random.choice(users)
            event = random.choice(events)

            span = event.end_time - event.start_time_and_date
            if span.total_seconds() < 1800:
                continue
            minutes_slot = random.randint(0, int(span.total_seconds() // 1800)) * 30
            time_slot = event.start_time_and_date + timedelta(minutes=minutes_slot)

            # ensure timezone-aware
            if timezone.is_naive(time_slot):
                time_slot = timezone.make_aware(time_slot, timezone.get_current_timezone())

            # no double-book
            if Reservation.objects.filter(user=user, time_and_date=time_slot).exists():
                continue

            svc_choices = list(event.services.all())
            chosen_services = random.sample(svc_choices, k=random.randint(1, len(svc_choices)))
            avail_pros = [p for p in pros if all(s in p.services.all() for s in chosen_services)]
            if not avail_pros:
                continue
            professional = random.choice(avail_pros)

            res = Reservation.objects.create(
                username=user.username,
                email=user.email,
                time_and_date=time_slot,
                event=event,
                professional=professional,
                user=user
            )
            res.services.set(chosen_services)
            created += 1

        self.stdout.write(f"Created {created} reservations.")

        self.stdout.write("Creating reviews for past attended events…")
        reviews = 0
        for res in Reservation.objects.filter(time_and_date__lt=now):
            if random.choice([True, False]):
                rv = Review.objects.create(
                    user=res.user,
                    username=res.username,
                    title=fake.sentence(nb_words=4),
                    text=fake.paragraph(nb_sentences=2),
                    event=res.event,
                    stars=random.randint(1,5)
                )
                if res.services.exists():
                    rv.services.set(random.sample(list(res.services.all()), k=random.randint(0, res.services.count())))
                reviews += 1

        self.stdout.write(self.style.SUCCESS(
            f"DB populated: {len(users)} users, {len(services)} services, {len(pros)} pros, {len(events)} events, {created} reservations, {reviews} reviews"
        ))
