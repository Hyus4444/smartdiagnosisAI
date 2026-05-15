/*Este archivo contiene funciones para interactuar con la API relacionada con los pacientes. Incluye funciones para listar pacientes y crear nuevos pacientes. 
Estas funciones utilizan el cliente HTTP configurado en src/config/api.js para realizar las solicitudes a la API y evitar hacer el consumo de la API en las pantallas*/
import api from "../config/api";

export async function listPatients({ skip = 0, limit = 20, q } = {}) {
  const res = await api.get("/patients", { params: { skip, limit, q } });
  return res.data; // { items, total, skip, limit }
}

export async function createPatient(payload) {
  // payload: { full_name, document_type, document_number, birth_date, gender }
  const res = await api.post("/patients", payload);
  return res.data;
}
