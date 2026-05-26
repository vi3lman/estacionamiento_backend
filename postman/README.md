# Postman - API Estacionamiento

Importar en Postman:

1. `Estacionamiento.local.postman_environment.json`
2. `00_Demo_Completa.postman_collection.json`
3. Opcionalmente, los archivos individuales dentro de `apis/`

Usar el ambiente `Estacionamiento - Local` y ejecutar el backend en:

```bash
uvicorn app.main:app --reload
```

La coleccion `00_Demo_Completa` esta ordenada para una demostracion completa:

1. Crea una calle unica.
2. Crea un espacio para esa calle.
3. Consulta calles, espacios y espacios libres.
4. Crea una ocupacion futura.
5. Guarda automaticamente `calleId`, `espacioId`, `ocupacionId` y `conductorId`.
6. Modifica y cancela una ocupacion con mas de 8 horas de anticipacion.
7. Crea otra ocupacion corta y espera unos segundos antes de finalizarla.

Notas:

- El endpoint `POST /espacios/{id_espacio}/infraccion` solo devuelve `200` si ya existe una ocupacion confirmada y vencida para ese espacio. Si no existe, devuelve `404`, que tambien queda contemplado como caso valido.
- Los archivos de `apis/` son colecciones separadas por modulo para importar solo lo que necesites en una demo puntual.
