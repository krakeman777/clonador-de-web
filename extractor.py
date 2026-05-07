import os
import re
import shutil
from pywebcopy import save_webpage

def procesar_y_limpiar(ruta_index, carpeta_final):
    """Ajusta el HTML para portabilidad total."""
    with open(ruta_index, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Fix de Rutas: Elimina rutas absolutas para que funcionen en Vercel y Local
    html = html.replace('src="/', 'src="./')
    html = html.replace('href="/', 'href="./')
    
    # 2. Fix de Protocolos: Asegura que recursos externos carguen siempre por HTTPS
    html = re.sub(r'src="//', 'src="https://', html)
    html = re.sub(r'href="//', 'href="https://', html)

    # 3. Parche de Estabilidad: Inyecta jQuery CDN y oculta preloaders que se quedan pegados
    patch = """
    <style>
        #preloader, .loader, .loading-screen { display: none !important; }
        body { opacity: 1 !important; overflow: visible !important; }
    </style>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    """
    html = html.replace('</head>', f'{patch}</head>')

    with open(ruta_index, 'w', encoding='utf-8') as f:
        f.write(html)

def preparar_para_despliegue(url, destino_base):
    proyecto_temp = "temp_raw"
    dist_folder = os.path.join(destino_base, "dist")
    
    # Descarga limpia
    kwargs = {'project_name': proyecto_temp, 'bypass_robots': True, 'open_in_browser': False}
    save_webpage(url, destino_base, **kwargs)

    # Buscar el index.html en la estructura de pywebcopy
    ruta_temp = os.path.join(destino_base, proyecto_temp)
    for root, dirs, files in os.walk(ruta_temp):
        if "index.html" in files:
            # Encontramos la carpeta real con los assets
            fuente_recursos = root
            
            # Mover todo a la carpeta /dist (Aplanamiento)
            if os.path.exists(dist_folder): shutil.rmtree(dist_folder)
            shutil.copytree(fuente_recursos, dist_folder)
            
            # Parchear el HTML final
            procesar_y_limpiar(os.path.join(dist_folder, "index.html"), dist_folder)
            break

    # Limpieza: borrar carpeta temporal de pywebcopy
    shutil.rmtree(ruta_temp)
    return dist_folder

if __name__ == "__main__":
    target = input("URL a clonar: ")
    path = os.getcwd()
    
    print("\n📦 Clonando y optimizando para Vercel/Local...")
    resultado = preparar_para_despliegue(target, path)
    
    print(f"\n✅ ¡LISTO! Todo está en la carpeta: {resultado}")
    print("🚀 Para Vercel: Sube el contenido de 'dist' o haz 'vercel deploy' dentro.")