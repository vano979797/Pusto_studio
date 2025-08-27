import csv
from datetime import datetime

from django.utils import timezone

from .second_task_models import (
    LevelPrize,
    PlayerLevel,
    PlayerPrize
)


def grant_prizes_for_level(player_level: PlayerLevel):
    """
    Присвоение игроку приза за прохождение уровня.
    """
    if not player_level.is_completed:
        raise ValueError("Уровень пока мал")

    level_prizes = (
        LevelPrize.objects
        .filter(level=player_level.level)
        .exclude(
            prize__in=PlayerPrize.objects.filter(
                player=player_level.player,
                level=player_level.level
            ).values('prize')
        )
        .select_related("prize")
    )

    received_prizes = []

    for prize in level_prizes:
        already_exists = PlayerPrize.objects.filter(
            player=player_level.player,
            prize=prize.prize,
            level=player_level.level
        ).exists()
        if already_exists:
            continue

        pp = PlayerPrize.objects.create(
            player=player_level.player,
            prize=prize.prize,
            level=player_level.level,
            received_at=timezone.now()
        )
        received_prizes.append(pp)

    return received_prizes

def import_player_levels_from_csv(file_path: str):
    """
    Выгрузку в csv данных играка и его уровней

    параметры:
    - id игрока,
    - название уровня,
    - пройден ли уровень,
    - полученный приз за уровень
    """
    new_records = []
    update_records = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            player_id = row['player_id']
            level_id = row['level_id']

            completed_date = None
            if row.get('completed_date'):
                completed_date = datetime.strptime(row['completed_date'], "%Y-%m-%d").date()

            is_completed = row.get('is_completed', '').lower() in ['true', '1', 'yes']
            score = int(row.get('score', '0'))

            try:
                existing = PlayerLevel.objects.get(
                    player_id=player_id,
                    level_id=level_id
                )
                existing.completed = completed_date
                existing.is_completed = is_completed
                existing.score = score
                update_records.append(existing)

            except PlayerLevel.DoesNotExist:
                new_record = PlayerLevel(
                    player_id=player_id,
                    level_id=level_id,
                    completed=completed_date,
                    is_completed=is_completed,
                    score=score
                )
                new_records.append(new_record)

            if len(new_records) >= 1000:
                PlayerLevel.objects.bulk_create(new_records)
                new_records = []

            if len(update_records) >= 1000:
                PlayerLevel.objects.bulk_update(
                    update_records,
                    ['completed', 'is_completed', 'score']
                )

                update_records = []

            if new_records:
                PlayerLevel.objects.bulk_create(new_records)

            if update_records:
                PlayerLevel.objects.bulk_update(
                    update_records,
                    ['completed', 'is_completed', 'score']
                )
