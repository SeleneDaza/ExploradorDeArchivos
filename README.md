# Explorador de Archivos

Explorador de archivos de escritorio desarrollado con Python y PyQt5, orientado a productividad y organización visual. Ofrece una interfaz moderna con soporte para múltiples temas, vista previa de archivos y personalización visual por ítem.

---

## Requisitos del sistema

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | 3.10 o superior (se recomienda 3.12) |
| Sistema operativo | Windows 10/11, Linux, macOS |

---

## Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repositorio>
cd ExploradorDeArchivos
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias obligatorias

```bash
pip install -r requirements.txt
```

`requirements.txt` contiene:

```
PyQt5==5.15.9
```

### 4. Instalar dependencias opcionales

Estas dependencias amplían las capacidades de vista previa. La aplicación funciona sin ellas, pero algunas características quedarán deshabilitadas.

```bash
pip install PyMuPDF          # Vista previa de archivos PDF
pip install opencv-python    # Miniatura de fotograma en videos
pip install mutagen          # Duración y metadatos de audio
```

| Paquete | Funcion |
|---------|---------|
| `PyMuPDF` | Renderiza la primera pagina de archivos `.pdf` en el panel de vista previa |
| `opencv-python` | Extrae un fotograma representativo de archivos de video |
| `mutagen` | Muestra duracion, bitrate y metadatos de archivos de audio |

---

## Ejecucion

```bash
python main.py
```

---

## Estructura del proyecto

```
ExploradorDeArchivos/
|
+-- main.py                        # Punto de entrada
|
+-- assets/
|   +-- icons/                     # Iconos de la interfaz (PNG, Lucide Icons)
|
+-- core/                          # Logica de negocio (sin dependencias de UI)
|   +-- filesystem.py              # Navegacion de directorios e historial
|   +-- operations.py              # Copiar, mover, renombrar, eliminar, crear
|   +-- permissions.py             # Lectura y escritura de permisos (chmod/chown)
|   +-- personalizer.py            # Etiquetas de color e insignias por archivo
|
+-- ui/                            # Interfaz grafica
|   +-- theme.py                   # Paletas de color, tokens de diseno, zoom
|   +-- icons.py                   # Cargador y tintador de iconos PNG
|   +-- main_window.py             # Ventana principal e integracion de componentes
|   +-- toolbar.py                 # Barra de herramientas con iconos del sistema
|   +-- file_tree.py               # Vista de arbol + lista con ordenamiento y filtros
|   |
|   +-- delegates/
|   |   +-- file_delegate.py       # Dibuja color e insignia sobre cada item
|   |
|   +-- dialogs/
|   |   +-- name_dialog.py         # Dialogo reutilizable para nombres
|   |   +-- folder_picker_dialog.py# Selector interno de carpeta destino
|   |   +-- personalize_dialog.py  # Selector de color e insignia por archivo
|   |   +-- permissions_dialog.py  # Editor de permisos
|   |   +-- properties_dialog.py   # Propiedades del archivo
|   |   +-- compare_dialog.py      # Comparacion de archivos
|   |
|   +-- widgets/
|       +-- favorites_panel.py     # Panel lateral de ubicaciones favoritas
|       +-- preview_panel.py       # Panel de vista previa con metadatos
|       +-- search_bar.py          # Barra de busqueda por nombre
|       +-- my_personalizations.py # Gestion de personalizaciones guardadas
|
+-- requirements.txt
```

---

## Funcionalidades

### Navegacion
- Arbol de directorios en el panel izquierdo con navegacion por clic
- Historial de navegacion con botones Atras / Adelante
- Barra de ruta (breadcrumb) clickeable para saltar a cualquier nivel
- Acceso rapido a Inicio, Raiz del sistema y carpetas favoritas
- Atajos de teclado: `Alt+izquierda` atras, `Alt+derecha` adelante, `Alt+arriba` subir, `Ctrl+H` inicio

### Gestion de archivos
- Crear carpetas y archivos con dialogo propio temático
- Copiar y mover con selector visual de carpeta destino integrado en la aplicacion
- Renombrar con valor prellenado
- Eliminar con confirmacion (individual o multiples)
- Seleccion multiple con `Ctrl+clic` y `Shift+clic`
- Abrir archivos con la aplicacion predeterminada del sistema operativo (doble clic)

### Visualizacion
- **Vista grilla**: iconos grandes en cuadricula (vista por defecto)
- **Vista lista**: filas compactas con iconos pequenos
- Cambio entre vistas desde la barra de ordenamiento
- Ordenamiento por Nombre, Tamano, Tipo o Fecha (ascendente y descendente)

### Vista previa
- Imagenes: renderizado a escala con dimensiones en pixeles
- PDF: primera pagina renderizada (requiere `PyMuPDF`)
- Texto y codigo: con resaltado de sintaxis para Python, JavaScript, HTML, CSS, JSON, YAML, Shell y mas
- Video: fotograma miniatura y duracion (requiere `opencv-python`)
- Audio: duracion y bitrate (requiere `mutagen`)
- Metadatos: ruta completa, fechas de creacion y modificacion, tamano, contador de aperturas
- Panel ocultable con `Ctrl+P` y animacion de desplazamiento
- Boton de fijar para mantener la vista previa aunque se cambie de archivo

### Busqueda
- Filtrado en tiempo real por nombre o extension desde la barra superior
- Atajo `Ctrl+F` para enfocar la busqueda
- Limpiar con `Esc`

### Personalizacion visual de archivos
- Asignar una **etiqueta de color** a cualquier archivo o carpeta (8 colores: rojo, naranja, amarillo, verde, azul, morado, rosa, gris)
- Asignar una **insignia** con significado semantico:
  - Favorito (estrella)
  - Importante (rombo)
  - Privado (circulo)
  - En progreso (semicirculo)
  - Finalizado (marca de verificacion)
- Los indicadores se dibujan sobre el item sin modificar ni reemplazar el icono del sistema de archivos
- **Filtro rapido por color** desde la barra de ordenamiento: los items sin esa etiqueta se difuminan
- Panel **Mis Personalizaciones** para ver, navegar y limpiar etiquetas de forma masiva
- Las personalizaciones persisten entre sesiones
- Al renombrar o mover un archivo dentro del explorador, la personalizacion se migra automaticamente a la nueva ruta


### Permisos
- Visualizacion de permisos en formato simbolico (rwxrwxrwx) y octal
- Edicion interactiva con checkboxes por categoria (propietario, grupo, otros)
- Cambio de propietario y grupo en Linux/macOS

### Temas visuales
- **Oscuro**: fondo negro profundo con acento indigo (inspirado en Linear y VS Code)
- **Claro**: fondo blanco con acento indigo (inspirado en Notion y macOS)
- **Retro**: paleta calida pastel con crema, coral y dorado
- Ciclo de temas con el boton de la barra de herramientas (Oscuro -> Claro -> Retro)

### Zoom de interfaz
- Escala proporcional de toda la interfaz: texto, iconos, espaciados, alturas de paneles
- Atajos: `Ctrl+=` ampliar, `Ctrl+-` reducir, `Ctrl+0` restablecer al 100%

### Favoritos
- Panel lateral con accesos directos a carpetas frecuentes
- Incluye Inicio, Documentos, Descargas e Imagenes por defecto
- Agregar la carpeta actual con un clic
- Quitar favoritos individualmente
- Persiste entre sesiones

---

## Atajos de teclado

| Atajo | Accion |
|-------|--------|
| `Ctrl+F` | Enfocar barra de busqueda |
| `Ctrl+N` | Nueva carpeta |
| `Ctrl+Shift+N` | Nuevo archivo |
| `F2` | Renombrar seleccionado |
| `Delete` | Eliminar seleccionado |
| `Ctrl+P` | Mostrar / ocultar panel de vista previa |
| `Ctrl+H` | Ir a carpeta personal |
| `Alt+Izquierda` | Atras en el historial |
| `Alt+Derecha` | Adelante en el historial |
| `Alt+Arriba` | Subir un nivel |
| `Ctrl+=` | Aumentar zoom |
| `Ctrl+-` | Reducir zoom |
| `Ctrl+0` | Restablecer zoom al 100% |
| `Esc` | Limpiar busqueda o deseleccionar |

---

## Archivos de datos del usuario

La aplicacion guarda configuracion y cache en:

```
~/.explorador_cache/
    personalizations.json    Etiquetas de color e insignias por archivo
    open_counts.json         Contador de aperturas por archivo
```

Estos archivos se crean automaticamente en el primer uso. No requieren configuracion manual. Pueden eliminarse de forma segura para restablecer los valores por defecto.

---

## Notas de compatibilidad

- En **Windows**, la apertura de archivos usa `os.startfile()`.
- En **Linux y macOS**, la apertura usa `xdg-open` y `open` respectivamente.
- Los permisos `chmod` y `chown` tienen efecto completo en **Linux y macOS**. En Windows se aplican unicamente los bits disponibles a traves de `os.chmod`.
- La vista previa de PDF requiere `PyMuPDF`. Sin el, se muestra un mensaje de tipo desconocido.
- La miniatura de video requiere `opencv-python`. Sin el, se muestra el nombre del archivo sin imagen.
