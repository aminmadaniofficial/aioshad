import pytest
from aioshad.fsm import FSMContext, MemoryStorage, SQLiteStorage, State, StatesGroup


class UserForm(StatesGroup):
    name = State()
    age = State()


@pytest.mark.asyncio
async def test_fsm_memory_storage():
    storage = MemoryStorage()
    ctx = FSMContext(storage, chat_id="g0chat_guid", user_id="u0author_guid")

    assert await ctx.get_state() is None

    await ctx.set_state(UserForm.name)
    assert await ctx.get_state() == UserForm.name.state

    await ctx.update_data(name="Ali")
    data = await ctx.get_data()
    assert data["name"] == "Ali"

    await ctx.clear()
    assert await ctx.get_state() is None
    assert await ctx.get_data() == {}


@pytest.mark.asyncio
async def test_fsm_sqlite_storage(tmp_path):
    db_file = tmp_path / "fsm_test.db"
    storage = SQLiteStorage(db_file)
    ctx = FSMContext(storage, chat_id="g0chat_sqlite", user_id="u0author_sqlite")

    await ctx.set_state(UserForm.age)
    assert await ctx.get_state() == UserForm.age.state

    await ctx.update_data(age=25)
    data = await ctx.get_data()
    assert data["age"] == 25

    await ctx.clear()
    assert await ctx.get_state() is None
