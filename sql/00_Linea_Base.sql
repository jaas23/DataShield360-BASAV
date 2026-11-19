/* =====================================================================
   PROYECTO FINAL BASAV - Distribuidora Andina Comercial S.A.C.
   Script 00: Línea base cuantitativa (Tabla 1 del Capítulo I)

   Cada consulta reproduce un indicador de la Tabla 1, organizado por
   dimensión del problema. P1-P4 = problemas del caso; DP = diagnóstico propio.
   Ejecutar ANTES de crear procedimientos, triggers, roles y backups
   (es la foto del "antes").
   ===================================================================== */
USE DistribuidoraAndina;
GO

/* =========================== 0. CONTEXTO ============================ */

-- Comprobantes, ventas y ticket promedio 2025 (solo EMITIDAS): 128 597 / 69 493 784.02 / 540.40
SELECT COUNT(*)   AS Comprobantes2025,
       SUM(Total) AS Ventas2025,
       AVG(Total) AS TicketPromedio2025
FROM dbo.Venta
WHERE Estado = 'EMITIDA' AND YEAR(FechaVenta) = 2025;

-- Crecimiento anual (2025 vs 2024 = +15.5 %).
-- OJO: 2026 sale negativo porque solo tiene enero-octubre (año incompleto).
WITH A AS (
    SELECT YEAR(FechaVenta) AS Anio, SUM(Total) AS Ventas
    FROM dbo.Venta WHERE Estado = 'EMITIDA'
    GROUP BY YEAR(FechaVenta))
SELECT Anio, Ventas,
       CAST(100.0 * (Ventas - LAG(Ventas) OVER (ORDER BY Anio))
            / LAG(Ventas) OVER (ORDER BY Anio) AS DECIMAL(6,1)) AS CrecimientoPct
FROM A ORDER BY Anio;

-- Crecimiento con periodos equivalentes: ene-oct 2026 vs ene-oct 2025 (+12.9 %)
WITH A AS (
    SELECT YEAR(FechaVenta) AS Anio, SUM(Total) AS Ventas
    FROM dbo.Venta
    WHERE Estado = 'EMITIDA' AND MONTH(FechaVenta) <= 10 AND YEAR(FechaVenta) IN (2025, 2026)
    GROUP BY YEAR(FechaVenta))
SELECT MAX(CASE WHEN Anio = 2025 THEN Ventas END) AS EneOct2025,
       MAX(CASE WHEN Anio = 2026 THEN Ventas END) AS EneOct2026,
       CAST(100.0 * (MAX(CASE WHEN Anio = 2026 THEN Ventas END)
                   / MAX(CASE WHEN Anio = 2025 THEN Ventas END) - 1) AS DECIMAL(6,1)) AS CrecimientoPct
FROM A;

-- Participación por sede (Lima 51.1 / Arequipa 26.7 / Trujillo 22.2)
SELECT s.Ciudad,
       SUM(v.Total) AS Ventas,
       CAST(100.0 * SUM(v.Total) / SUM(SUM(v.Total)) OVER () AS DECIMAL(5,1)) AS ParticipacionPct
FROM dbo.Venta v
JOIN dbo.Sucursal s ON s.SucursalID = v.SucursalID
WHERE v.Estado = 'EMITIDA'
GROUP BY s.Ciudad
ORDER BY Ventas DESC;

-- Estacionalidad 2025 (diciembre 8.92 M vs febrero 4.20 M = 2.1 veces)
SELECT MONTH(FechaVenta) AS Mes, COUNT(*) AS Comprobantes, SUM(Total) AS Ventas
FROM dbo.Venta
WHERE Estado = 'EMITIDA' AND YEAR(FechaVenta) = 2025
GROUP BY MONTH(FechaVenta)
ORDER BY Mes;

-- Usuarios operativos por cargo y sede (total 55: 26 vendedores, 14 choferes,
-- 8 almaceneros, 4 supervisores, 3 administradores de sede)
SELECT e.Cargo,
       SUM(CASE WHEN s.Ciudad = 'Lima'     THEN 1 ELSE 0 END) AS Lima,
       SUM(CASE WHEN s.Ciudad = 'Arequipa' THEN 1 ELSE 0 END) AS Arequipa,
       SUM(CASE WHEN s.Ciudad = 'Trujillo' THEN 1 ELSE 0 END) AS Trujillo,
       COUNT(*) AS Total
FROM dbo.Empleado e
JOIN dbo.Sucursal s ON s.SucursalID = e.SucursalID
GROUP BY e.Cargo
ORDER BY Total DESC;

-- Titulares de datos personales (Ley N.° 29733 protege a personas naturales):
-- 1 114 clientes personas naturales (368 DNI + 746 RUC 10) y 55 colaboradores.
-- Los 1 286 clientes con RUC 20 son empresas (personas jurídicas).
SELECT SUM(CASE WHEN TipoDocumento = 'DNI' THEN 1 ELSE 0 END)                               AS ClientesConDNI,
       SUM(CASE WHEN TipoDocumento = 'RUC' AND NumeroDocumento LIKE '10%' THEN 1 ELSE 0 END) AS ClientesRUC10,
       SUM(CASE WHEN TipoDocumento = 'DNI'
                 OR (TipoDocumento = 'RUC' AND NumeroDocumento LIKE '10%') THEN 1 ELSE 0 END) AS ClientesPersonasNaturales,
       SUM(CASE WHEN TipoDocumento = 'RUC' AND NumeroDocumento LIKE '20%' THEN 1 ELSE 0 END) AS ClientesEmpresas,
       (SELECT COUNT(*) FROM dbo.Empleado)                                                    AS Colaboradores
FROM dbo.Cliente;

/* =========================== 1. INTEGRIDAD ========================== */

-- [P1] Procedimientos almacenados creados por el usuario: 0
SELECT COUNT(*) AS ProcedimientosAlmacenados
FROM sys.procedures
WHERE is_ms_shipped = 0;

-- [DP] Restricciones declarativas: PK 9 / FK 12 / CHECK 11 / UNIQUE 9
SELECT (SELECT COUNT(*) FROM sys.key_constraints WHERE type = 'PK') AS PK,
       (SELECT COUNT(*) FROM sys.foreign_keys)                       AS FK,
       (SELECT COUNT(*) FROM sys.check_constraints)                  AS [CHECK],
       (SELECT COUNT(*) FROM sys.key_constraints WHERE type = 'UQ') AS [UNIQUE];

-- [DP] Distritos con formato inconsistente: 143 (6.0 %)
--      DATALENGTH detecta espacios al final (el operador = los ignora en SQL Server).
--      COLLATE ..._CS_ hace la comparación sensible a mayúsculas/minúsculas.
SELECT COUNT(*) AS DistritosInconsistentes,
       CAST(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dbo.Cliente) AS DECIMAL(5,1)) AS Pct
FROM dbo.Cliente
WHERE DATALENGTH(Distrito) <> DATALENGTH(LTRIM(RTRIM(Distrito)))
   OR Distrito COLLATE Latin1_General_CS_AS = UPPER(Distrito)
   OR Distrito COLLATE Latin1_General_CS_AS = LOWER(Distrito);

--      Ejemplos (los corchetes muestran los espacios sobrantes)
SELECT TOP (20) ClienteID, '[' + Distrito + ']' AS DistritoConBordes
FROM dbo.Cliente
WHERE DATALENGTH(Distrito) <> DATALENGTH(LTRIM(RTRIM(Distrito)))
   OR Distrito COLLATE Latin1_General_CS_AS = UPPER(Distrito)
   OR Distrito COLLATE Latin1_General_CS_AS = LOWER(Distrito);

-- [DP] Clientes sin email / sin teléfono: 25.0 % / 8.5 %
SELECT COUNT(*) AS Clientes,
       SUM(CASE WHEN Email IS NULL THEN 1 ELSE 0 END) AS SinEmail,
       CAST(100.0 * SUM(CASE WHEN Email IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(5,1)) AS PctSinEmail,
       SUM(CASE WHEN Telefono IS NULL THEN 1 ELSE 0 END) AS SinTelefono,
       CAST(100.0 * SUM(CASE WHEN Telefono IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(5,1)) AS PctSinTelefono
FROM dbo.Cliente;

-- [DP] Comprobantes anulados: 5 258 (1.46 %)
SELECT COUNT(*) AS Comprobantes,
       SUM(CASE WHEN Estado = 'ANULADA' THEN 1 ELSE 0 END) AS Anulados,
       CAST(100.0 * SUM(CASE WHEN Estado = 'ANULADA' THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(5,2)) AS PctAnulados
FROM dbo.Venta;

/* ========================== 2. TRAZABILIDAD ========================= */

-- [P1] Triggers de auditoría y tablas auditadas: 0 / 0 de 9
SELECT (SELECT COUNT(*) FROM sys.triggers WHERE is_ms_shipped = 0)                         AS Triggers,
       (SELECT COUNT(DISTINCT parent_id) FROM sys.triggers WHERE parent_class = 1)         AS TablasConTrigger,
       (SELECT COUNT(*) FROM sys.tables WHERE is_ms_shipped = 0)                           AS TablasTotales;

/* ============================ 3. SEGURIDAD ========================== */

-- [P2] Backups registrados de la base: 0 (UltimoBackup = NULL)
SELECT COUNT(*) AS BackupsRegistrados, MAX(backup_finish_date) AS UltimoBackup
FROM msdb.dbo.backupset
WHERE database_name = 'DistribuidoraAndina';

--      Modelo de recuperación (FULL permite backups de log en el paso 3)
SELECT name, recovery_model_desc FROM sys.databases WHERE name = 'DistribuidoraAndina';

-- [P4] Roles de base de datos personalizados: 0
SELECT COUNT(*) AS RolesPersonalizados
FROM sys.database_principals
WHERE type = 'R' AND is_fixed_role = 0 AND name <> 'public';

--      Usuarios de la base distintos de los del sistema (dbo, guest, sys, INFORMATION_SCHEMA)
SELECT name, type_desc
FROM sys.database_principals
WHERE type IN ('S', 'U', 'G', 'E', 'X') AND principal_id > 4;

-- [P4] Columnas con datos personales: 9 (5 en Cliente, 4 en Empleado)
SELECT TABLE_NAME AS Tabla, COLUMN_NAME AS Columna
FROM INFORMATION_SCHEMA.COLUMNS
WHERE (TABLE_NAME = 'Cliente'  AND COLUMN_NAME IN ('NumeroDocumento', 'RazonSocial', 'Direccion', 'Telefono', 'Email'))
   OR (TABLE_NAME = 'Empleado' AND COLUMN_NAME IN ('DNI', 'Nombres', 'Apellidos', 'Email'))
ORDER BY Tabla, Columna;

--      Columnas con enmascaramiento dinámico (Dynamic Data Masking): 0
SELECT COUNT(*) AS ColumnasEnmascaradas FROM sys.masked_columns;

/* =================== 4. OPORTUNIDAD DE LA INFORMACIÓN =============== */

-- [P3] Tiempo de respuesta de una consulta analítica sobre la base OLTP
--      (medición inicial del experimento EXP-01: OLTP vs. data warehouse)
--
--      CÓMO MEDIR:
--      1. Selecciona SOLO este bloque (desde SET STATISTICS hasta el último OFF) y presiona F5.
--      2. Ve a la pestaña "Messages" y busca la línea que aparece DESPUÉS de las filas del SELECT:
--            SQL Server Execution Times:
--               CPU time = ___ ms,  elapsed time = ___ ms.
--         Anota el "elapsed time" (tiempo transcurrido) de esa línea, no el de CHECKPOINT o DBCC.
--      3. Repite 3 veces y reporta la MEDIANA (el valor del medio).
--      DBCC DROPCLEANBUFFERS vacía la caché de datos para medir en frío.
--      Úsalo solo en entornos de prueba, nunca en producción.
SET STATISTICS TIME ON;
CHECKPOINT;
DBCC DROPCLEANBUFFERS;

SELECT YEAR(v.FechaVenta)  AS Anio,
       MONTH(v.FechaVenta) AS Mes,
       s.Ciudad,
       c.Nombre            AS Categoria,
       SUM(d.Cantidad)     AS Unidades,
       SUM(d.Subtotal)     AS VentaNeta
FROM dbo.Venta v
JOIN dbo.DetalleVenta d ON d.VentaID     = v.VentaID
JOIN dbo.Producto p     ON p.ProductoID  = d.ProductoID
JOIN dbo.Categoria c    ON c.CategoriaID = p.CategoriaID
JOIN dbo.Sucursal s     ON s.SucursalID  = v.SucursalID
WHERE v.Estado = 'EMITIDA'
GROUP BY YEAR(v.FechaVenta), MONTH(v.FechaVenta), s.Ciudad, c.Nombre
ORDER BY Anio, Mes, s.Ciudad, Categoria;

SET STATISTICS TIME OFF;

/* ======================= 5. VOLUMEN Y VARIEDAD ====================== */

-- [DP] Filas transaccionales acumuladas: 1 956 687 (DetalleVenta: 1 251 129)
SELECT (SELECT COUNT(*) FROM dbo.Venta)
     + (SELECT COUNT(*) FROM dbo.DetalleVenta)
     + (SELECT COUNT(*) FROM dbo.Despacho)
     + (SELECT COUNT(*) FROM dbo.Cliente)
     + (SELECT COUNT(*) FROM dbo.Inventario) AS FilasTransaccionales;

/* ===================== 6. CONSECUENCIAS OPERATIVAS ================== */

-- [DP] Despachos entregados a tiempo: 84.89 % de 340 702
SELECT COUNT(*) AS Entregados,
       SUM(CASE WHEN CAST(FechaEntrega AS DATE) <= FechaProgramada THEN 1 ELSE 0 END) AS ATiempo,
       CAST(100.0 * SUM(CASE WHEN CAST(FechaEntrega AS DATE) <= FechaProgramada THEN 1 ELSE 0 END)
            / COUNT(*) AS DECIMAL(5,2)) AS PctATiempo
FROM dbo.Despacho
WHERE Estado = 'ENTREGADO';

-- [DP] Posiciones de inventario (sede + producto) bajo el stock mínimo: 26 de 198
SELECT COUNT(*) AS Posiciones,
       SUM(CASE WHEN StockActual < StockMinimo THEN 1 ELSE 0 END) AS BajoMinimo
FROM dbo.Inventario;

--      Detalle: qué productos y en qué sede
SELECT s.Ciudad, p.Nombre, i.StockActual, i.StockMinimo
FROM dbo.Inventario i
JOIN dbo.Sucursal s ON s.SucursalID = i.SucursalID
JOIN dbo.Producto p ON p.ProductoID = i.ProductoID
WHERE i.StockActual < i.StockMinimo
ORDER BY s.Ciudad, i.StockActual;
GO
