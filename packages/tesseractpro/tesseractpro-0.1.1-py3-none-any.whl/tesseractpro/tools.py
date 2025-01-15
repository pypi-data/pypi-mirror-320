from .base import Base
from .decorators.on import on


class Tools (Base):
    @on("tool:add")
    def on_tools_added(self, data) -> None:
        self.emit('add', data)

    @on("tool:update")
    def on_tool_update(self, data) -> None:
        self.emit('update', data)

    @on("tool:remove")
    def on_tool_remove(self, data) -> None:
        self.emit('remove', data)

    def get_tools(
            self,
            from_unix: int,
            to_unix: int,
            timeframe: int,
            market: str,
            space_id: str
    ):
        """
        Return tools for the given parameters
        """
        data = self._tpro.rest.post("tools", {
            "to": to_unix,
            "from": from_unix,
            "timeframe": timeframe * 60,
            "market": market,
            "space_id": space_id
        })
        return {item['id']: item for item in data}
