from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ClaveProdServ(Base):
    __tablename__ = "clave_prod_serv"
    c_ClaveProdServ = Column(String, primary_key=True)
    Descripcion = Column(String)
    Incluir_IVA_trasladado = Column(String)
    Incluir_IEPS_trasladado = Column(String)
    Complemento_que_debe_incluir = Column(String)
    FechaInicioVigencia = Column(DateTime)
    FechaFinVigencia = Column(DateTime)
    Estimulo_Franja_Fronteriza = Column(String)
    Palabras_similares = Column(String)


class Classification(Base):
    __tablename__ = "classification"
    tipo_num = Column(Integer)
    Tipo = Column(String)
    Div_num = Column(Integer)
    Division = Column(String)
    Grupo_num = Column(Integer)
    Grupo = Column(String)
    Clase_num = Column(Integer, primary_key=True)
    Clase = Column(String)
