import pandas as pd
import numpy as np
from typing import List, Dict, Any

class ControlDato:
    """
    Motor principal de revisiones ambientales para ACCIONA Concesiones.
    Analiza exclusivamente usando la clave primaria IdCentro + idKPI.
    """
    def __init__(self, df_normalizado: pd.DataFrame, historico_descargas: List[pd.DataFrame] = None):
        self.df = df_normalizado.copy()
        self.historico = historico_descargas if historico_descargas else []
        self.revisiones: List[Dict[str, Any]] = []

    def ejecutar_revisiones(self) -> pd.DataFrame:
        """Orquesta la ejecución de todas las reglas de control de datos."""
        self.revisiones = []
        
        self._aplicar_cr001_unidades()
        self._aplicar_cr002_desviacion_historica()
        self._aplicar_cr003_valores_repetidos()
        self._aplicar_cr005_coherencia_cruzada()
        self._aplicar_cr006_cambio_brusco()
        
        if self.historico:
            self._aplicar_cr004_kpis_desaparecidos()

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
        """Registra una incidencia estandarizada."""
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
        """CR001: Posible error de unidad o decimal (salto de orden de magnitud)."""
        for (id_centro, id_kpi), grupo in self.df.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 3:
                continue
            mediana = grupo['Cantidad'].median()
            if mediana == 0:
                continue

            for _, row in grupo.iterrows():
                val = row['Cantidad']
                ratio = val / mediana if mediana != 0 else 1
                if ratio > 50 or (ratio < 0.02 and val > 0):
                    self._registrar(
                        row, regla='CR001', categoria='Calidad de Dato',
                        val_ref=round(mediana, 2),
                        obs=f"El valor reportado ({val}) difiere sustancialmente de la mediana histórica del centro ({round(mediana, 2)}).",
                        accion="Verificar si se ha cambiado de unidad (ej. kg a toneladas) o si existe un error en la posición de decimales."
                    )

    def _aplicar_cr002_desviacion_historica(self):
        """CR002: Dato muy diferente al histórico usando Rango Intercuartílico (IQR)."""
        for (id_centro, id_kpi), grupo in self.df.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 4:
                continue
            q1 = grupo['Cantidad'].quantile(0.25)
            q3 = grupo['Cantidad'].quantile(0.75)
            iqr = q3 - q1
            mediana = grupo['Cantidad'].median()
            
            if iqr == 0:
                continue

            for _, row in grupo.iterrows():
                val = row['Cantidad']
                if abs(val - mediana) > (4 * iqr):
                    self._registrar(
                        row, regla='CR002', categoria='Comportamiento Atípico',
                        val_ref=round(mediana, 2),
                        obs=f"Valor ({val}) muy alejado del patrón habitual del centro (mediana histórica: {round(mediana, 2)}).",
                        accion="Confirmar con operaciones si ha ocurrido una incidencia extraordinaria o parada en el activo."
                    )

    def _aplicar_cr003_valores_repetidos(self):
        """CR003: Valor repetido idéntico durante varios periodos (consolidado)."""
        df_sorted = self.df.sort_values(by=['IdCentro', 'idKPI', 'Periodo'])
        for (id_centro, id_kpi), grupo in df_sorted.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 4:
                continue
            
            valores = grupo['Cantidad'].values
            periodos = grupo['Periodo'].values
            
            racha = 1
            val_racha = valores[0]
            inicio_racha = periodos[0]
            
            for i in range(1, len(valores)):
                if valores[i] == val_racha and val_racha != 0:
                    racha += 1
                else:
                    if racha >= 4:
                        row_ejemplo = grupo[grupo['Periodo'] == periodos[i-1]].iloc[0]
                        self._registrar(
                            row_ejemplo, regla='CR003', categoria='Estabilidad Sospechosa',
                            val_ref=f"Constante en {racha} periodos",
                            obs=f"Valor de {val_racha} reportado idénticamente durante {racha} periodos consecutivos (desde {inicio_racha}).",
                            accion="Comprobar si se está aplicando un valor estimado o lectura fija automática en el contador."
                        )
                    racha = 1
                    val_racha = valores[i]
                    inicio_racha = periodos[i]

    def _aplicar_cr004_kpis_desaparecidos(self):
        """CR004: KPI esperado no reportado (comparando con la última descarga histórica)."""
        if not self.historico:
            return
        df_previo = self.historico[-1]
        
        kpis_actuales = set(self.df[['IdCentro', 'idKPI']].itertuples(index=False, name=None))
        kpis_previos = set(df_previo[['IdCentro', 'idKPI']].itertuples(index=False, name=None))
        
        desaparecidos = kpis_previos - kpis_actuales
        for id_centro, id_kpi in desaparecidos:
            ejemplo = df_previo[(df_previo['IdCentro'] == id_centro) & (df_previo['idKPI'] == id_kpi)]
            if not ejemplo.empty:
                row = ejemplo.iloc[0]
                self._registrar(
                    row, regla='CR004', categoria='Trazabilidad de Descarga',
                    val_ref="Presente en descarga anterior",
                    obs=f"El KPI '{row.get('KPI')}' figuraba en descargas anteriores pero no aparece en el set de datos actual.",
                    accion="Verificar si el cierre de datos de este centro se ha retrasado o si el KPI ha sido dado de baja."
                )

    def _aplicar_cr005_coherencia_cruzada(self):
        """CR005: Coherencia lógica entre indicadores relacionados (ej. agua vs vertidos)."""
        for id_centro, grupo_centro in self.df.groupby('IdCentro'):
            for periodo, grupo_periodo in grupo_centro.groupby('Periodo'):
                agua = grupo_periodo[grupo_periodo['KPI'].str.contains('Agua|Captación', case=False, na=False)]
                vertido = grupo_periodo[grupo_periodo['KPI'].str.contains('Vertido', case=False, na=False)]
                
                if not agua.empty and not vertido.empty:
                    tot_agua = agua['Cantidad'].sum()
                    tot_vertido = vertido['Cantidad'].sum()
                    
                    if tot_agua > 0 and tot_vertido > (tot_agua * 1.3):
                        row_ref = vertido.iloc[0]
                        self._registrar(
                            row_ref, regla='CR005', categoria='Coherencia de Masas',
                            val_ref=f"Entrada: {round(tot_agua, 2)}",
                            obs=f"El volumen de vertidos ({round(tot_vertido, 2)}) supera en más de un 30% al agua captada ({round(tot_agua, 2)}).",
                            accion="Revisar posibles aportaciones de pluviales o errores en la medición de consumos de entrada."
                        )

    def _aplicar_cr006_cambio_brusco(self):
        """CR006: Cambio brusco respecto al periodo inmediatamente anterior."""
        df_sorted = self.df.sort_values(by=['IdCentro', 'idKPI', 'Periodo'])
        for (id_centro, id_kpi), grupo in df_sorted.groupby(['IdCentro', 'idKPI']):
            if len(grupo) < 2:
                continue
            
            cants = grupo['Cantidad'].values
            for i in range(1, len(cants)):
                val_ant = cants[i-1]
                val_act = cants[i]
                
                if val_ant > 5:
                    variacion = abs(val_act - val_ant) / val_ant
                    if variacion > 0.85:
                        row = grupo.iloc[i]
                        self._registrar(
                            row, regla='CR006', categoria='Variación Intermensual',
                            val_ref=round(val_ant, 2),
                            obs=f"Variación intermensual elevada del {round(variacion * 100, 1)}% (periodo previo: {round(val_ant, 2)} vs actual: {val_act}).",
                            accion="Validar si responde a estacionalidad operativa real o a un error de transcripción."
                        )