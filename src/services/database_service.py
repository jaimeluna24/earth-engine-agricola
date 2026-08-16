import os

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class DatabaseService:

    @staticmethod
    def conectar():

        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "db_mapas"),
            port=int(os.getenv("DB_PORT", 3306))
        )

    @staticmethod
    def guardar_ndvi(
        finca,
        lote,
        fecha_inicio,
        fecha_fin,
        datos
    ):

        conexion = DatabaseService.conectar()
        cursor = conexion.cursor()

        # Verificar si ya existe
        cursor.execute(
            """
            SELECT id
            FROM ndvi_lotes
            WHERE finca = %s
            AND lote = %s
            AND fecha_inicio = %s
            AND fecha_fin = %s
            LIMIT 1
            """,
            (
                finca,
                lote,
                fecha_inicio,
                fecha_fin
            )
        )

        existente = cursor.fetchone()

        valores = (
            datos["NDVI_min"],
            datos["NDVI_mean"],
            datos["NDVI_max"],
            datos["area_total"],
            datos["porcentaje_critico"],
            datos["porcentaje_bajo"],
            datos["porcentaje_medio"],
            datos["porcentaje_bueno"],
            datos["porcentaje_excelente"]
        )

        if existente:

            cursor.execute(
                """
                UPDATE ndvi_lotes
                SET
                    ndvi_min = %s,
                    ndvi_mean = %s,
                    ndvi_max = %s,
                    area_total = %s,
                    porcentaje_critico = %s,
                    porcentaje_bajo = %s,
                    porcentaje_medio = %s,
                    porcentaje_bueno = %s,
                    porcentaje_excelente = %s
                WHERE id = %s
                """,
                valores + (existente[0],)
            )

        else:

            cursor.execute(
                """
                INSERT INTO ndvi_lotes (
                    finca,
                    lote,
                    fecha_inicio,
                    fecha_fin,
                    ndvi_min,
                    ndvi_mean,
                    ndvi_max,
                    area_total,
                    porcentaje_critico,
                    porcentaje_bajo,
                    porcentaje_medio,
                    porcentaje_bueno,
                    porcentaje_excelente
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s,
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    finca,
                    lote,
                    fecha_inicio,
                    fecha_fin,
                    *valores
                )
            )

        conexion.commit()

        cursor.close()
        conexion.close()
             
    @staticmethod
    def obtener_ndvi(
        finca,
        fecha_inicio,
        fecha_fin
    ):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            finca as Finca,
            lote as Lote,
            fecha_fin as Fecha,

            ROUND(ndvi_min, 2) as Min,
            ROUND(ndvi_mean, 2) as Prom,
            ROUND(ndvi_max, 2) as Max,

            ROUND(area_total, 2) as Area,

            ROUND(porcentaje_critico, 2) as Crítico,
            ROUND(porcentaje_bajo, 2) as Bajo,
            ROUND(porcentaje_medio, 2) as Medio,
            ROUND(porcentaje_bueno, 2) as Bueno,
            ROUND(porcentaje_excelente, 2) as Excelente

        FROM ndvi_lotes

        WHERE finca = %s

        AND fecha_inicio = %s

        AND fecha_fin = %s

        ORDER BY lote
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(
                finca,
                fecha_inicio,
                fecha_fin
            )
        )

        conexion.close()

        return df
    
    @staticmethod
    def guardar_ndwi(
        finca,
        lote,
        fecha_inicio,
        fecha_fin,
        datos
    ):

        conexion = DatabaseService.conectar()

        cursor = conexion.cursor()

        sql = """
        INSERT INTO ndwi_lotes_stats (
            finca,
            lote,
            fecha_inicio,
            fecha_fin,

            ndwi_min,
            ndwi_mean,
            ndwi_max,

            area_total,

            porcentaje_muy_danado,
            porcentaje_danado,
            porcentaje_dano_moderado,
            porcentaje_estres,
            porcentaje_amarillo,
            porcentaje_transicion,
            porcentaje_vegetacion_moderada,
            porcentaje_vegetacion_saludable,
            porcentaje_saludable,
            porcentaje_muy_saludable
        )
        VALUES (
            %s, %s, %s, %s,

            %s, %s, %s,

            %s,

            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )

        ON DUPLICATE KEY UPDATE

            ndwi_min = VALUES(ndwi_min),
            ndwi_mean = VALUES(ndwi_mean),
            ndwi_max = VALUES(ndwi_max),

            area_total = VALUES(area_total),

            porcentaje_muy_danado =
                VALUES(porcentaje_muy_danado),

            porcentaje_danado =
                VALUES(porcentaje_danado),

            porcentaje_dano_moderado =
                VALUES(porcentaje_dano_moderado),

            porcentaje_estres =
                VALUES(porcentaje_estres),

            porcentaje_amarillo =
                VALUES(porcentaje_amarillo),

            porcentaje_transicion =
                VALUES(porcentaje_transicion),

            porcentaje_vegetacion_moderada =
                VALUES(porcentaje_vegetacion_moderada),

            porcentaje_vegetacion_saludable =
                VALUES(porcentaje_vegetacion_saludable),

            porcentaje_saludable =
                VALUES(porcentaje_saludable),

            porcentaje_muy_saludable =
                VALUES(porcentaje_muy_saludable)
        """

        valores = (
            finca,
            lote,
            fecha_inicio,
            fecha_fin,

            datos["NDWI_min"],
            datos["NDWI_mean"],
            datos["NDWI_max"],

            datos["area_total"],

            datos["porcentaje_muy_danado"],
            datos["porcentaje_danado"],
            datos["porcentaje_dano_moderado"],
            datos["porcentaje_estres"],
            datos["porcentaje_amarillo"],
            datos["porcentaje_transicion"],
            datos["porcentaje_vegetacion_moderada"],
            datos["porcentaje_vegetacion_saludable"],
            datos["porcentaje_saludable"],
            datos["porcentaje_muy_saludable"]
        )

        cursor.execute(
            sql,
            valores
        )

        conexion.commit()

        cursor.close()
        conexion.close()
        
    @staticmethod
    def obtener_ndwi(
        finca,
        fecha_inicio,
        fecha_fin
    ):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            finca as Finca,
            lote as Lote,
            fecha_fin as Fecha,

            ROUND(ndwi_min, 2) as Min,
            ROUND(ndwi_mean, 2) as Prom,
            ROUND(ndwi_max, 2) as Max,

            ROUND(area_total, 2) as Area,

            ROUND(porcentaje_muy_danado, 2) as "Estrés Crítico",
            ROUND(porcentaje_danado, 2) as "Estrés Severo",
            ROUND(porcentaje_dano_moderado, 2) as "Estrés Moderado",
            ROUND(porcentaje_estres, 2) as "Humedad Baja",
            ROUND(porcentaje_amarillo, 2) as "Humedad Optima",
            ROUND(porcentaje_transicion, 2) as "Vegetación Hidratada",
            ROUND(porcentaje_vegetacion_moderada, 2) as "Humedad Alta",
            ROUND(porcentaje_vegetacion_saludable, 2) as "Agua Muy Alta",
            ROUND(porcentaje_saludable, 2) as "Saturación de Agua",
            ROUND(porcentaje_muy_saludable, 2) as "Agua Abierta"
            
        FROM ndwi_lotes_stats

        WHERE finca = %s

        AND fecha_inicio = %s

        AND fecha_fin = %s

        ORDER BY lote
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(
                finca,
                fecha_inicio,
                fecha_fin
            )
        )

        conexion.close()

        return df    
    
    @staticmethod
    def guardar_ndre(
        finca,
        lote,
        fecha_inicio,
        fecha_fin,
        datos
    ):

        conexion = DatabaseService.conectar()

        cursor = conexion.cursor()

        sql = """
        INSERT INTO ndre_lotes (
            finca,
            lote,
            fecha_inicio,
            fecha_fin,

            ndre_min,
            ndre_mean,
            ndre_max,

            area_total,

            porcentaje_critico,
            porcentaje_bajo,
            porcentaje_medio,
            porcentaje_bueno,
            porcentaje_excelente
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s,
            %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE

            ndre_min = VALUES(ndre_min),
            ndre_mean = VALUES(ndre_mean),
            ndre_max = VALUES(ndre_max),

            area_total = VALUES(area_total),

            porcentaje_critico =
                VALUES(porcentaje_critico),

            porcentaje_bajo =
                VALUES(porcentaje_bajo),

            porcentaje_medio =
                VALUES(porcentaje_medio),

            porcentaje_bueno =
                VALUES(porcentaje_bueno),

            porcentaje_excelente =
                VALUES(porcentaje_excelente)
        """

        valores = (
            finca,
            lote,
            fecha_inicio,
            fecha_fin,

            datos["NDRE_min"],
            datos["NDRE_mean"],
            datos["NDRE_max"],

            datos["area_total"],

            datos["porcentaje_critico"],
            datos["porcentaje_bajo"],
            datos["porcentaje_medio"],
            datos["porcentaje_bueno"],
            datos["porcentaje_excelente"]
        )

        cursor.execute(
            sql,
            valores
        )

        conexion.commit()

        cursor.close()
        conexion.close()
        
    @staticmethod
    def obtener_ndre(
        finca,
        fecha_inicio,
        fecha_fin
    ):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            finca as Finca,
            lote as Lote,
            fecha_fin as Fecha,

            ROUND(ndre_min, 2) as Min,
            ROUND(ndre_mean, 2) as Prom,
            ROUND(ndre_max, 2) as Max,

            ROUND(area_total, 2) as Area,

            ROUND(porcentaje_critico, 2) as "Crítico",
            ROUND(porcentaje_bajo, 2) as "Bajo",
            ROUND(porcentaje_medio, 2) as "Medio",
            ROUND(porcentaje_bueno, 2) as "Bueno",
            ROUND(porcentaje_excelente, 2) as "Excelente"
            
        FROM ndre_lotes

        WHERE finca = %s

        AND fecha_inicio = %s

        AND fecha_fin = %s

        ORDER BY lote
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(
                finca,
                fecha_inicio,
                fecha_fin
            )
        )

        conexion.close()

        return df
    
    @staticmethod
    def obtener_historico_ndvi(finca):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            fecha_fin as Fecha,
            area_total as Area,
            ndvi_min as Min,
            ndvi_mean as Prom,
            ndvi_max as Max

        FROM ndvi_lotes

        WHERE finca = %s

        ORDER BY fecha_fin
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(finca,)
        )

        conexion.close()

        return df
    
    @staticmethod
    def obtener_historico_ndwi(finca):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            fecha_fin as Fecha,
            area_total as Area,
            ndwi_min as Min,
            ndwi_mean as Prom,
            ndwi_max as Max

        FROM ndwi_lotes_stats

        WHERE finca = %s

        ORDER BY fecha_fin
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(finca,)
        )

        conexion.close()

        return df    
    @staticmethod
    def obtener_historico_ndre(finca):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            fecha_fin as Fecha,
            area_total as Area,
            ndre_min as Min,
            ndre_mean as Prom,
            ndre_max as Max

        FROM ndre_lotes

        WHERE finca = %s

        ORDER BY fecha_fin
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(finca,)
        )

        conexion.close()

        return df   
    
    @staticmethod
    def obtener_ndvi_por_periodo(
        finca,
        fecha_inicio,
        fecha_fin
    ):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            n.*,
            m.fecha_cosecha

        FROM ndvi_lotes n

        LEFT JOIN maestro_lotes m
            ON m.lote = n.lote
            AND m.finca = n.finca

        WHERE n.finca = %s
        AND n.fecha_inicio = %s
        AND n.fecha_fin = %s

        ORDER BY n.lote
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(
                finca,
                fecha_inicio,
                fecha_fin
            )
        )

        conexion.close()

        return df   
    
    @staticmethod
    def obtener_ndwi_por_periodo(
        finca,
        fecha_inicio,
        fecha_fin
    ):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            n.*,
            m.fecha_cosecha

        FROM ndwi_lotes_stats n

        LEFT JOIN maestro_lotes m
            ON m.lote = n.lote
            AND m.finca = n.finca

        WHERE n.finca = %s
        AND n.fecha_inicio = %s
        AND n.fecha_fin = %s

        ORDER BY n.lote
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(
                finca,
                fecha_inicio,
                fecha_fin
            )
        )

        conexion.close()

        return df
    
    @staticmethod
    def obtener_ndre_por_periodo(
        finca,
        fecha_inicio,
        fecha_fin
    ):

        conexion = DatabaseService.conectar()

        sql = """
        SELECT
            n.*,
            m.fecha_cosecha

        FROM ndre_lotes n

        LEFT JOIN maestro_lotes m
            ON m.lote = n.lote
            AND m.finca = n.finca

        WHERE n.finca = %s
        AND n.fecha_inicio = %s
        AND n.fecha_fin = %s

        ORDER BY n.lote
        """

        df = pd.read_sql(
            sql,
            conexion,
            params=(
                finca,
                fecha_inicio,
                fecha_fin
            )
        )

        conexion.close()

        return df