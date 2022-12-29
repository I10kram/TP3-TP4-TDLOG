
from sqlalchemy import create_engine,Column,Integer,String,ForeignKey,select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship,sessionmaker
from model.weapon import Weapon
from model.battlefield import Battlefield
from model.vessel import Vessel
from model.game import Game
from model.player import Player



engine = create_engine('sqlite:////tmp/tdlog.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)



class GameEntity(Base):
  __tablename__ = 'game'
  id = Column(Integer, primary_key=True)
  players = relationship("PlayerEntity", back_populates="game",
  cascade="all, delete-orphan")

class PlayerEntity(Base):
  __tablename__ = 'player'
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
  game = relationship("GameEntity", back_populates="player")
  battlefield = relationship("BattlefieldEntity",
  back_populates="player",
  uselist=False, cascade="all, delete-orphan")

class BattlefieldEntity(Base):
   __tablename__ = 'battlefield'
   id=Column(Integer,primary_key=True,nullable=False )
   min_x=Column(Integer)
   min_y=Column(Integer)
   min_z=Column(Integer)
   max_x=Column(Integer)
   max_y=Column(Integer)
   max_z=Column(Integer)
   max_power=Column(Integer)
   player_id=Column(Integer,ForeignKey("player.id"),nullable=False)
   player=relationship("PlayerEntity",back_populates="battlefield")
   vessel=relationship("VesselEntity",back_populates="battlefield",uselist=True)
 

class VesselEntity(Base):
  _tablaname_='vessel'
  id=Column(Integer,primary_key=True,nullable=False )
  coord_x=Column(Integer)
  coord_y=Column(Integer)
  coord_z=Column(Integer)
  hits_to_be_destroyed=Column(Integer)
  type=Column(String)
  battlefield_id=Column(Integer,ForeignKey("battlefield.id"),nullable=False)
  battlefield=relationship("BattlefieldEntiy",back_populates="vessel", 
  uselist=False, cascade="all, delete-orphan") 
  weapon=relationship("WeaponEntity",back_populates="vessel")
  

class WeaponEntity(Base):
  _tablename_='weapon'
  id=Column(Integer,primary_key=True,nullable=False )
  ammunitions=Column(Integer)
  range=Column(Integer)
  type=Column(String)
  vessel_id=Column(Integer,ForeignKey("vessel.id"),nullable=False)
  vessel=relationship("VesselEntity",back_populates="weapon",uselist=True)


      

     

class GameDao:
      def __init__(self):
           Base.metadata.create_all()
           self.db_session = Session()
   
      def create_game(self, game:Game) -> int:
           game_entity = self.map_to_game_entity(game)
           self.db_session.add(game_entity)
           self.db_session.commit()
           return game_entity.id
      def create_vessel(self, battlefield_id: int, vessel: Vessel) -> int:
            vessel_entity = self.map_to_vessel_entity(battlefield_id, vessel)
            self.db_session.add(vessel_entity)
            self.db_session.commit()
            return vessel_entity.id

      def create_player(self, player: Player, game_id) -> int:
        player_entity = self.map_to_player_entity(player, game_id)
        self.db_session.add(player_entity)
        self.db_session.commit()
        return player_entity.id

      def find_game(self, game_id: int):
            stmt = select(GameEntity).where(GameEntity.id == game_id)
            game_entity = self.db_session.scalars(stmt).one()
            return self.map_to_game(game_entity)

      def find_vessel(self, vessel_id: int) -> Vessel:
            stmt = select(VesselEntity).where(VesselEntity.id == vessel_id)
            vessel_entity = self.db_session.scalars(stmt).one()
            return self.map_to_vessel(vessel_entity)

      def find_player(self, player_id: int) -> Player:
        stmt = select(PlayerEntity).where(PlayerEntity.id == player_id)
        player_entity = self.db_session.scalars(stmt).one()
        return self.map_to_player(player_entity)

      def map_to_vessel_entity(self,battlefield_id: int, vessel:Vessel) -> VesselEntity:
         vessel_entity = VesselEntity()
         weapon_entity = WeaponEntity()
         weapon_entity.id = vessel.weapon.id
         weapon_entity.ammunitions = vessel.weapon.ammunitions
         weapon_entity.range = vessel.weapon.range
         weapon_entity.type = type(vessel.weapon).__name__,
         vessel_entity.id = vessel.id
         vessel_entity.weapon = weapon_entity
         vessel_entity.type = type(vessel).__name__
         vessel_entity.hits_to_be_destroyed = vessel.hits_to_be_destroyed
         vessel_entity.coord_x = vessel.coordinates[0]
         vessel_entity.coord_y = vessel.coordinates[1]
         vessel_entity.coord_z = vessel.coordinates[2]
         vessel_entity.battle_field_id = battlefield_id
         return vessel_entity


      def map_to_vessel_entities(self,battlefield_id: int, vessels: list[Vessel]) \
        -> list[VesselEntity]:
        vessel_entities: list[VesselEntity] = []
        for vessel in vessels:
              vessel_entity =self.map_to_vessel_entity(battlefield_id,vessel)
              vessel_entities.append(vessel_entity)

        return vessel_entities

      
      def map_to_game_entity(self,game) -> GameEntity:
           game_entity = GameEntity()
           if game.get_id() is not None:
                game_entity.id = game.get_id()
           for player in game.get_players():
               player_entity = PlayerEntity()
               player_entity.id = player.id
               player_entity.name = player.get_name()
               battlefield_entity = self.map_to_battlefield_entity(
                     player.get_battlefield())
               vessel_entities = self.map_to_vessel_entities(player.get_battlefield().id,
                                   player.get_battlefield().vessels)
                           
               battlefield_entity.vessels = vessel_entities
               player_entity.battle_field = battlefield_entity
               game_entity.players.append(player_entity)
           return game_entity

   

      def map_to_battlefield_entity(battlefield: Battlefield) -> BattlefieldEntity:
        battlefield_entity = BattlefieldEntity()
        battlefield_entity.id = battlefield.id
        battlefield_entity.max_x = battlefield.max_x
        battlefield_entity.max_y = battlefield.max_y
        battlefield_entity.max_z = battlefield.max_z
        battlefield_entity.min_x = battlefield.min_x
        battlefield_entity.min_y = battlefield.min_y
        battlefield_entity.min_z = battlefield.min_z
        battlefield_entity.max_power = battlefield.max_power
        return battlefield_entity

    



      def map_to_player_entity(self,player) -> PlayerEntity:
         player_entity = PlayerEntity()
         player_entity.id = player.id
         player_entity.name = player.name
         player_entity.battle_field = self.map_to_battlefield_entity(player.get_battlefield())
         return player_entity

      def map_to_battlefield(battlefield_entity: BattlefieldEntity) -> Battlefield:
        min_x = battlefield_entity.min_x
        max_x = battlefield_entity.max_x
        min_y = battlefield_entity.min_y
        max_y = battlefield_entity.max_y
        min_z = battlefield_entity.min_z
        max_z = battlefield_entity.max_z
        max_power = battlefield_entity.max_power
        battlefield = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z, max_power)
        return battlefield
      
      def map_to_player(self,player_entity) -> Player:
        name = player_entity.name
        battle_field = self.map_to_battlefield(player_entity.battle_field)
        player = Player(name, battle_field)
        player.id = player_entity.id
        return player

      def map_to_game(self,game_entity: GameEntity) -> Game:
        if game_entity.id is not None:
          game = Game(game_entity.id)
        for player_entity in game_entity.players:
          player = self.map_to_player(player_entity)
          game.add_player(player)
        return game

      def map_to_vessel(vessel_entity: VesselEntity) -> Vessel:
        x = vessel_entity.coord_x
        y = vessel_entity.coord_y
        z = vessel_entity.coord_z
        hits = vessel_entity.hits_to_be_destroyed
        ammunition = vessel_entity.weapon.ammunitions
        rayon = vessel_entity.weapon.range
        weapon = Weapon(ammunition, rayon)
        vessel = Vessel(x, y, z, hits, weapon)
        return vessel
     

     


      
  
      
      

     