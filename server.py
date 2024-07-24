import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Session, Advertisement, engine, Base

app = web.Application()

def get_http_error(error_class, message):
    response = json.dumps({"error": message})
    http_error = error_class(text=response, content_type="application/json")

    return http_error

async def add_advertisement(session, advertisement):
    try:
        session.add(advertisement)
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise get_http_error(web.HTTPConflict, f"Advertisement with header {advertisement.header} already exists")

async def orm_context(app: web.Application):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app.cleanup_ctx.append(orm_context)

async def get_advertisement_by_id(session, advertisement_id):
    advertisement = await session.get(Advertisement, advertisement_id)

    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, f"Advertisement with id {advertisement_id} not found")
    
    return advertisement

@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response
    
app.middlewares.append(session_middleware)


class AdvertisementView(web.View):
    @property
    def advertisement_id(self):
        return int(self.request.match_info["advertisement_id"])
    
    @property
    def session(self):
        return self.request.session
    
    async def get_advertisement(self):
        advertisement = await get_advertisement_by_id(self.session, self.advertisement_id)
        return advertisement

    async def get(self):
        advertisement = await self.get_advertisement()

        return web.json_response(advertisement.dict)

    async def post(self):
        json_data = await self.request.json()

        advertisement = Advertisement(**json_data)
        await add_advertisement(self.session, advertisement)
        
        return web.json_response({
            "id": advertisement.id
        })

    async def patch(self):
        json_data = await self.request.json()

        advertisement = await self.get_advertisement()

        for field, value in json_data.items():
            setattr(advertisement, field, value)

        await add_advertisement(self.session, advertisement)

        return web.json_response({
            "id": advertisement.id
        })

    async def delete(self):
        advertisement = await self.get_advertisement()
        await self.session.delete(advertisement)
        await self.session.commit()

        return web.json_response({"status": "deleted"})


app.add_routes([
    web.get("/advertisement/{advertisement_id:\d+}/", AdvertisementView),
    web.patch("/advertisement/{advertisement_id:\d+}/", AdvertisementView),
    web.delete("/advertisement/{advertisement_id:\d+}/", AdvertisementView),
    web.post("/advertisement/", AdvertisementView),
])

web.run_app(app)
