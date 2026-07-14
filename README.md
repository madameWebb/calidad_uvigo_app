# Calidade UVIGO

Aplicación web para a xestión de indicadores de calidade da Universidade de Vigo, desenvolvida como proxecto de prácticas no Área de Calidade da UVIGO.

## Tecnoloxías

- **Backend**: Python 3.14 / Django 5.2
- **Base de datos**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Librarías**: openpyxl, django-simple-history

## Funcionalidades

### Vistas públicas
- Consulta de **centros**, **títulos** e **indicadores** de calidade
- **Seguimentos** de centros e títulos por curso académico
- **Avaliacións do PDI** por titulación
- **Materias avaliadas** e os seus seguimentos
- Filtros de busca, ordenamento e agrupación

### Área de xestión (Admin)
- Xestión completa de todos os modelos
- Historial de cambios (django-simple-history)
- Filtros e buscadores avanzados
- Importación masiva de datos desde Excel

### Scripts de importación
Ferramentas para importar datos desde os Excel do cadro de mando:
- `importar_indicadores` — indicadores e relacións con centros/títulos
- `importar_seguimentos_centros` — seguimentos dos centros
- `importar_seguimentos_materias` — seguimentos das materias
- `importar_pdis` — avaliacións do PDI
- `importar_materias` — materias avaliadas
- `importar_codigos` — códigos SIGMA das titulacións

### Ferramentas de auditoría
Scripts standalone para verificar a integridade dos datos importados:
- `auditar_seguimentos.py`
- `auditar_pdis.py`
- `auditar_materias.py`
- `auditar_seguimentos_materias.py`

## Instalación

```bash
# Clonar o repositorio
git clone https://github.com/madameWebb/calidad_uvigo_app.git
cd calidad_uvigo_app

# Crear e activar entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos en config/settings.py

# Aplicar migracións
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Arrancar servidor
python manage.py runserver
```

## Estrutura do proxecto

calidad_uvigo_app/
├── config/          # Configuración Django
├── gestion/
│   ├── management/
│   │   └── commands/    # Scripts de importación
│   ├── migrations/      # Migracións da BD
│   ├── static/          # CSS, JS, imaxes
│   ├── templates/       # Templates HTML
│   ├── admin.py         # Configuración do admin
│   ├── models.py        # Modelos de datos
│   ├── urls.py          # URLs
│   └── views.py         # Vistas
├── *.py             # Scripts de auditoría
└── manage.py


## Modelos principais

- **Centros / Titulos / Codigos** — estrutura académica da UVIGO
- **Indicadores** — indicadores de calidade (institucional, estratéxico, calidade)
- **IRPD** — Informe de Revisión pola Dirección
- **Seguimentos / SeguimentosTitulos** — seguimento de indicadores por curso
- **AvaliacionsPdis** — avaliación do PDI por titulación
- **MateriasAvaliadas / SeguementoMaterias** — seguimento por materia

## Autora

Virginia García Álvarez — Proxecto de prácticas CIFP Coia (Vigo)  
Universidade de Vigo — Área de Calidade
