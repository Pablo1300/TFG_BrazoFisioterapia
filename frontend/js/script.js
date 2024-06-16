const articulations = document.getElementById("articulation")
const movements = document.getElementById("movement")
const endfeels = document.getElementById("endfeel")
const range = document.getElementById("executionPoint")
const simulateButton = document.getElementById("simulateButton")

// Función encargada de activar la variable de punto de ejecución si la articulacion y el movimiento estan seleccionados
function activateExecutionPoint() {
    // Si en el select de movimientos no hay ningun valor elegido
    if (movements.value === "disabled") {
        range.disabled = true;
        range.nextElementSibling.querySelector('output').value = "Selecciona articulación y movimiento para calcular rango de movimiento"
    } else { // Si en el select de movimientos hay algun valor elegido
        range.disabled = false;
        // Variable de articulaciones y sus movimientos con su rango de movimiento
        let executionPointList = {
            hombro: [[-60, 180, "flexext"], [0, 180, "abdadu"], [-90, 90, "intext"]],
            codo: [[-7, 140, "flexext"]],
        }
        // Si la articulación elegida es el hombro...
        if (articulations.value === "hombro") {
            // Se agrega el rango y valor del movimiento seleccionado
            executionPointList.hombro.forEach(function (executionPoint) {
                if (movements.value === executionPoint[2]) {
                    range.min = executionPoint[0]
                    range.max = executionPoint[1]
                }
            })
        } else { // Si la articulación elegida es el codo...
            // Se agrega el rango y valor del movimiento disponibñe
            range.min = executionPointList.codo[0][0]
            range.max = executionPointList.codo[0][1]
        }
        range.value = 0
        range.nextElementSibling.querySelector('output').value = range.value

        document.getElementById("grado").style.display = "block"
    }
}

articulations.addEventListener("change", function () {
    activateExecutionPoint()

    // Variable de articulaciones con sus respectivos movimientos
    let movementList = {
        hombro: [["Flexión/Extensión", "flexext"], ["Abducción/Aducción", "abdadu"], ["Rotación Interna/Externa", "intext"]],
        codo: [["Flexión/Extensión", "flexext"]],
    }
    // Se obtiene el valor seleccionado en articulaciones
    let articulationSelected = articulations.value

    // Se limpia el select de movimientos
    movements.innerHTML = '<option value="disabled" disabled selected>Selecciona tipo de movimiento...</option>'

    // Si la articulación seleccionada no es null
    if (articulationSelected !== '') {
        // Se seleccionan los movimientos de dicha articulacion
        articulationSelected = movementList[articulationSelected]

        // Se insertan los movimientos
        articulationSelected.forEach(function (movement) {
            let option = document.createElement('option')
            option.value = movement[1]
            option.text = movement[0]
            movements.add(option)
        });
    }
})

movements.addEventListener("change", function () {
    activateExecutionPoint()
})

simulateButton.addEventListener("click", function (event) {
    let movementSelected = movements.value
    let endFeelSelected = endfeels.value
    let executionPoint = range.value

    let errorMovement = document.getElementById("error-movement")
    let errorEndFeel = document.getElementById("error-endfeel")
    let errorRange = document.getElementById("error-range")

    if (movementSelected === "disabled") {
        errorMovement.style.display = "block"
        event.preventDefault()
    } else {
        errorMovement.style.display = "none";
    }

    if (endFeelSelected === "disabled") {
        errorEndFeel.style.display = "block"
        event.preventDefault()
    } else {
        errorEndFeel.style.display = "none"
    }

    if (executionPoint == 0) {
        errorRange.style.display = "block"
        event.preventDefault()
    } else {
        errorRange.style.display = "none"
    }
})