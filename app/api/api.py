import json
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Vehicle, VehicleResponse


def read_user():
    with open('data/users.json', encoding='utf-8') as stream:
        users = json.load(stream)
    return users


def read_questions(position: int):
    with open('data/questions.json', encoding='utf-8') as stream:
        questions = json.load(stream)
    for question in questions:
        if question['position'] == position:
            return question


def read_alternatives(question_id: int):
    alternatives_question = []
    with open('data/alternatives.json', encoding='utf-8') as stream:
        alternatives = json.load(stream)
    for alternative in alternatives:
        if alternative['question_id'] == question_id:
            alternatives_question.append(alternative)
    return alternatives_question


def create_answer(payload):
    answers = []
    result = []

    with open('data/alternatives.json', encoding='utf-8') as stream:
        alternatives = json.load(stream)

    # C1 fix: match both question_id AND alternative_id so the user's actual
    # selection is used, not always the first alternative for each question.
    for question in payload['answers']:
        for alternative in alternatives:
            if (alternative['question_id'] == question['question_id']
                    and alternative['id'] == question['alternative_id']):
                answers.append(alternative['alternative'])
                break

    with open('data/cars.json', encoding='utf-8') as stream:
        cars = json.load(stream)

    for car in cars:
        if answers[0] in car.values() and answers[1] in car.values() and answers[2] in car.values():
            result.append(car)

    return result


def read_result(user_id: int):
    user_result = []

    with open('data/results.json', encoding='utf-8') as stream:
        results = json.load(stream)

    with open('data/users.json', encoding='utf-8') as stream:
        users = json.load(stream)

    with open('data/cars.json', encoding='utf-8') as stream:
        cars = json.load(stream)

    for result in results:
        if result['user_id'] == user_id:
            for user in users:
                if user['id'] == result['user_id']:
                    user_result.append({'user': user})
                    break

            # C2 fix: car lookup must be inside the user_id guard so only
            # the matched user's cars are appended, not every user's cars.
            for car_id in result['cars']:
                for car in cars:
                    if car_id == car['id']:
                        user_result.append(car)

    return user_result


def get_vehicle_by_id(vehicle_id: int, db: Session) -> Optional[VehicleResponse]:
    """Return vehicle details from the ORM database by primary key - FR-001."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None:
        return None
    return VehicleResponse.model_validate(vehicle)
