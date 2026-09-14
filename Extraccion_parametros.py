



def permutar_semilla_circular(semilla_actual):
    """
    Realiza un desplazamiento circular a la izquierda de los dígitos de la semilla.

    Ejemplo: 1658743 -> 6587431
    """
    # 1. Convertir el entero a una cadena para manipular los dígitos
    semilla_str = str(semilla_actual)

    # 2. Extraer el primer dígito
    primer_digito = semilla_str[0]

    # 3. Obtener el resto de la cadena (desde el segundo dígito hasta el final)
    resto_digitos = semilla_str[1:]

    # 4. Concatenar: poner el resto delante del primer dígito
    nueva_semilla_str = resto_digitos + primer_digito

    # 5. Convertir la nueva cadena de vuelta a un entero y devolverla
    nueva_semilla = int(nueva_semilla_str)

    return nueva_semilla



def cargar_param(nombre_archivo):
    configuracion = {}
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if '=' in linea:
                # Divide la línea en clave y valor
                clave, valor = linea.split('=', 1)
                configuracion[clave.strip()] = valor.strip()
    return configuracion