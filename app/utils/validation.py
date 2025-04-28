from fastapi import HTTPException


async def raise_if_duplicate(repo, session, field_value_pairs, model=None):
    """
    Checks for duplicates and raises an exception with a dynamic message if found.
    :param repo: The repository instance from the repositores module
    :param session: The DB session
    :param field_value_pairs: List of (field, value) tuples
    :param model: The SQLAlchemy model class (optional, inferred if not provided)
    """
    duplicate = await repo.exists_by_fields(session, field_value_pairs)

    if duplicate:
        field, value = duplicate
        # Get model if not provided
        if model is None:
            model = getattr(field, "class_", None)

        model_name = model.__name__ if model else "Object"
        field_name = field.key if hasattr(field, "key") else str(field)
        message = f"A {model_name} with this {field_name} already exists."

        message = message.format(model=model_name, field=field_name)

        raise HTTPException(status_code=409, detail=message)
