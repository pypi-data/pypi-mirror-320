from sqlmodel import select


class BaseFilter:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def filter(self, query: 'select') -> 'select':
        """Applies filters to the query. Override in child classes for custom filtering."""
        for key, value in self.__dict__.items():
            if value is not None:
                field = getattr(self.model, key, None)
                if field:
                    query = query.where(field == value)
        return query

    def sort(self, query: 'select', sort_field: str, ascending: bool = True) -> 'select':
        """Sorts the query results based on a sort_field and direction."""
        if sort_field:
            if ascending:
                query = query.order_by(getattr(self.model, sort_field))
            else:
                query = query.order_by(getattr(self.model, sort_field).desc())
        return query
