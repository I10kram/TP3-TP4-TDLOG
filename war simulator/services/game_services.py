from dao.gamedao import GameDao
from sqlalchemy import select, update
from model.game import Game
from dao.gamedao import GameDao, PlayerEntity, WeaponEntity, VesselEntity
from model.battlefield import Battlefield
from model.player import Player


class GameService:
 def __init__(self):
   self.game_dao = GameDao()

 def create_game(self, player_name: str, min_x: int, max_x: int, min_y: int,
   max_y: int, min_z: int, max_z: int) -> int:
   game = Game()
   battle_field = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z)
   game.add_player(Player(player_name, battle_field))
   return self.game_dao.create_game(game)

 def join_game(self, game_id: int, player_name: str) -> bool:
   game=self.create_game(game_id)
   player=Player(player_name)
   add=self.game_dao.create_player(player, game)
   if not add:
        return False
   return True

 def get_game(self, game_id: int) -> Game:
  return self.game_dao.find_game(game_id)

 def add_vessel(self, game_id: int, player_name: str, vessel_type: str,
 x: int, y: int, z: int) -> bool:
   vessel=vessel_type(x,y,z)
   game = self.create_game(game_id)
   for player in game.get_players():
                a=player.get_battlefield().add_vessel(vessel)
                if vessel in player.get_battlefield().get_vessels():
                    b = select(PlayerEntity).where(PlayerEntity.name == player_name and PlayerEntity.game_id == game_id)
                    player_entity = self.db_session.scalars(b).one()
                    b= select(Battlefield).where(Battlefield.player_id == player_entity.id)
                    battlefield_entity = self.db_session.scalars(b).one()
                    self.game_dao.create_vessel(battlefield_entity.id, vessel)
                    return True
                else:
                    return False



 def shoot_at(self, game_id: int, shooter_name: str, vessel_id: int, x: int, y: int, z: int) -> bool:
        vessel = self.game_dao.find_vessel(vessel_id)
        game = self.game_dao.find_game(game_id)
        if vessel.weapon.ammunitions >= 1:
            c = update(WeaponEntity).where(WeaponEntity.vessel_id == vessel_id).values(
                {WeaponEntity.ammunitions: WeaponEntity.ammunitions - 1})
            self.db_session.scalars(c).one()
            for player in game.get_players():
                if player.get_name() != shooter_name:
                    if player.get_battlefield().fired_at(x, y, z):
                        d = update(VesselEntity).where(VesselEntity.coord_x == x, VesselEntity.coord_y == y, VesselEntity.coord_z == z).values(
                            {VesselEntity.hits_to_be_destroyed: VesselEntity.hits_to_be_destroyed - 1})
                        self.db_session.scalars(d).one()
                        return True
                    return False

 def get_game_status(self, game_id: int, shooter_name: str) -> str:
        game = self.game_dao.find_game(game_id)
        for player in game.get_players():
            if player.get_name() == shooter_name:
                if player.get_battlefield().get_vessels() is None:
                    return "PERDU"
            elif player.get_battlefield().get_vessels() is None:
                return "GAGNE"
        return "ENCOURS"
