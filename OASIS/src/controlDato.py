"""
controlDato.py
Motor de reglas de control ambiental para ACCIONA Concesiones.
"""
import pandas as pd
from typing import List, Dict, Any

class ControlDato:
    def __init__(self, df_normalizado: pd.DataFrame, historico_descargas: List[pd.DataFrame] = None):
        self.df = df_normalizado.copy()
        self.historico = historico_descargas if historico_descargas else []
        self.revisiones: List[Dict[str, Any]] = []

    def ejecutar_revisiones(self) -> pd.DataFrame:
        self.revisiones = []
        self._aplicar_cr001_unidades()
        self._aplicar_cr002_desviacion_historica()
        self._aplicar_cr003_valores_repetidos()
        self._aplicar_cr005_coherencia_cruzada()
        self._aplicar_cr006_cambio_brusco()

        columnas_salida = [
            'Proyecto', 'Centro', 'Regla', 'Categoria', 'TipoDato', 
            'KPI', 'Periodo', 'Valor', 'ValorReferencia', 'Observacion', 
            'Accion', 'Estado', 'ComentarioUsuario'
        ]

        if not self.revisiones:
            return pd.DataFrame(columns=columnas_salida)

        df_res = pd.DataFrame(self.revisiones)
        df_res['Estado'] = 'Pendiente'
        df_res['ComentarioUsuario'] = ''
        return df_res[columnas_salida]

    def _registrar(self, row: pd.Series, regla: str, categoria: str, val_ref: Any, obs: str, accion: str):
        self.revisiones.append({
            'Proyecto': row.get('CodigoNegocio', 'N/D'),
            'Centro': row.get('Centro', 'N/D'),
            'Regla': regla,
            'Categoria': categoria,
            'TipoDato': row.get('Tipo_Dato', 'N/D'),
            'KPI': row.get('KPI', 'N/D'),
            'Periodo': row.get('Periodo', 'N/D'),
            'Valor': row.get('Cantidad', 0.0),
            'ValorReferencia': val_ref,
            'Observacion': obs,
            'Accion': accion
        })

    def _aplicar_cr001_unidades(self):
        for (_, _), grupo in self.df.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 3: continue
            mediana = grupo['Cantidad'].median()
            if mediana == 0: continue
            for _, row in grupo.iterrows():
                val = row['Cantidad']
                ratio = val / mediana
                if ratio > 50 or (ratio < 0.02 and val > 0):
                    self._registrar(row, 'CR001', 'Calidad de Dato', round(mediana, 2), f"Valor ({val}) difiere de la mediana ({round(mediana, 2)}).", "Verificar unidad o decimales.")

    def _aplicar_cr002_desviacion_historica(self):
        for (_, _), grupo in self.df.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 4: continue
            q1, q3 = grupo['Cantidad'].quantile(0.25), grupo['Cantidad'].quantile(0.75)
            iqr, mediana = q3 - q1, grupo['Cantidad'].median()
            if iqr == 0: continue
            for _, row in grupo.iterrows():
                if abs(row['Cantidad'] - mediana) > (4 * iqr):
                    self._registrar(row, 'CR002', 'Comportamiento Atípico', round(mediana, 2), f"Valor atípico respecto a la mediana ({round(mediana, 2)}).", "Confirmar parada o incidencia.")

    def _aplicar_cr003_valores_repetidos(self):
        df_sorted = self.df.sort_values(by=['IdCentro', 'idKPI', 'Periodo'])
        for (_, _), grupo in df_sorted.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 4: continue
            valores, periodos = grupo['Cantidad'].values, grupo['Periodo'].values
            racha, val_racha, inicio_racha = 1, valores[0], periodos[0]
            for i in range(1, len(valores)):
                if valores[i] == val_racha and val_racha != 0:
                    racha += 1
                else:
                    if racha >= 4:
                        self._registrar(grupo[grupo['Periodo'] == periodos[i-1]].iloc[0], 'CR003', 'Estabilidad Sospechosa', f"Constante {racha} periodos", f"Valor repetido idéntico desde {inicio_racha}.", "Comprobar lectura fija.")
                    racha, val_racha, inicio_racha = 1, valores[i], periodos[i]

    def _aplicar_cr005_coherencia_cruzada(self):
        for _, grupo_centro in self.df.groupby('IdCentro'):
            for _, grupo_periodo in grupo_centro.groupby('Periodo'):
                agua = grupo_periodo[grupo_periodo['KPI'].str.contains('Agua|Captación', case=False, na=False)]
                vertido = grupo_periodo[grupo_periodo['KPI'].str.contains('Vertido', case=False, na=False)]
                if not agua.empty and not vertido.empty:
                    tot_agua, tot_vertido = agua['Cantidad'].sum(), vertido['Cantidad'].sum()
                    if tot_agua > 0 and tot_vertido > (tot_agua * 1.3):
                        self._registrar(vertido.iloc[0], 'CR005', 'Coherencia de Masas', f"Entrada: {round(tot_agua, 2)}", f"Vertido ({round(tot_vertido, 2)}) supera al agua.", "Revisar pluviales o consumos.")

    def _aplicar_cr006_cambio_brusco(self):
        df_sorted = self.df.sort_values(by=['IdCentro', 'idKPI', 'Periodo'])
        for (_, _), grupo in df_sorted.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 2: continue
            cants = grupo['Cantidad'].values
            for i in range(1, len(cants)):
                val_ant, val_act = cants[i-1], cants[i]
                if val_ant > 0 and (abs(val_act - val_ant) / val_ant) > 0.85:
                    self._registrar(grupo.iloc[i], 'CR006', 'Variación Intermensual', round(val_ant, 2), f"Variación intermensual alta respecto a {round(val_ant, 2)}.", "Validar estacionalidad u error.")