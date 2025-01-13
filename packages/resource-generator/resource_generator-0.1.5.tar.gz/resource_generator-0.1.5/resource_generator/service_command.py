import typer
from resource_generator.cli_factory import __create_file
app = typer.Typer(no_args_is_help=True)

@app.command()
def name(service_name: str):
    """Create a new service file."""
    template = f"""import uuid


from app.core.base_response import AppResponseAsList, AppResponse
from app.core.filter_params import FilterParams
from app.exceptions.base_exception import AppExceptionHandler
from app.schemas.person_schema import {service_name.capitalize()}Request, {service_name.capitalize()}Response, {service_name.capitalize()}Update
from app.repository import {service_name.capitalize()}RepositoryDep


class {service_name.capitalize()}Service:
    def __init__(
        self,
        person_repo: {service_name.capitalize()}RepositoryDep
    ):
        self.person_repo = person_repo

    async def create(self, body: {service_name.capitalize()}Request) -> AppResponse[{service_name.capitalize()}Response]:
        try:
            response = self.person_repo.create(obj_in=body)
            return AppResponse(
                data=response,
                message="Create successful"
            )
        except AppExceptionHandler as e:
            raise RuntimeError(f"Error while creating: {{e}}")

    async def list(self, filter_params: FilterParams) -> AppResponseAsList[{service_name.capitalize()}Response]:
        try:
            response = self.person_repo.list(filter_params=filter_params)
            return AppResponseAsList(data=response)
        except AppExceptionHandler as e:
            raise f"Error while get as list {{e}}"

    async def update(self, person_id: uuid.UUID,  body: {service_name.capitalize()}Update):
        try:
            person_obj = self.person_repo.get_by_id(person_id)
            response = self.person_repo.update(db_obj=person_obj, obj_in=body)
            return AppResponse(data=response, message="Update success")
        except AppExceptionHandler as e:
            raise f"Error while update {{e}}"

    async def delete(self, recode_id):
        try:
            response = self.person_repo.remove(_id=recode_id)
            return AppResponse(data=response, message="Delete success")
        except AppExceptionHandler as e:
            raise f"Error while delete {{e}}"
    """

    __create_file("services", f"{service_name.lower()}", "_service.py", template)

