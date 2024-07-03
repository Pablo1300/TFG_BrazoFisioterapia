const articulations = document.getElementById("articulation")
const movements = document.getElementById("movement")
const endfeels = document.getElementById("endfeel")
const range = document.getElementById("executionPoint")
const simulateButton = document.getElementById("simulateButton")
const stopButton = document.getElementById("stopButton")
const ip = "localhost"

// Función encargada de activar la variable de punto de ejecución si la articulacion y el movimiento estan seleccionados
function activateExecutionPoint() {
    // Si en el select de movimientos no hay ningun valor elegido
    if (movements.value === "disabled") {
        range.disabled = true
        range.nextElementSibling.querySelector('output').value = "Selecciona articulación y movimiento para calcular rango de movimiento"
        document.getElementById("grado").style.display = "none"
    } else { // Si en el select de movimientos hay algun valor elegido
        range.disabled = false
        // Variable de articulaciones y sus movimientos con su rango de movimiento
        let executionPointList = {
            hombro: [[-60, 180, "flexext"], [0, 180, "abdadu"], [-90, 90, "intext"]],
            codo: [[-5, 140, "flexext"]],
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

// Se añade al select de articulation las acciones cuando cambie
articulations.addEventListener("change", function () {
    // Variable de articulaciones con sus respectivos movimientos
    let movementList = {
        hombro: [["Flexión/Extensión", "flexext"], ["Abducción/Aducción", "abdadu"], ["Rotación Interna/Externa", "intext"]],
        codo: [["Flexión/Extensión", "flexext"]],
    }
    // Se obtiene el valor seleccionado en articulaciones
    let articulationSelected = articulations.value

    if (articulationSelected === 'codo') {
        // Se limpia el select de movimientos
        movements.innerHTML = '<option value="disabled" disabled>Selecciona tipo de movimiento...</option>'
    }

    if (articulationSelected === 'hombro') {
        // Se limpia el select de movimientos
        movements.innerHTML = '<option value="disabled" disabled selected>Selecciona tipo de movimiento...</option>'
    }

    // Si la articulación seleccionada no es null
    if (articulationSelected !== '') {
        // Se seleccionan los movimientos de dicha articulacion
        articulationSelected = movementList[articulationSelected]

        // Se insertan los movimientos
        articulationSelected.forEach(function (movement) {
            let option = document.createElement('option')
            option.value = movement[1]
            option.text = movement[0]
            if (articulationSelected === 'codo') option.selected = true
            movements.add(option)
        })
    }
    activateExecutionPoint()
})

// Se añade al select de movement las acciones cuando cambie
movements.addEventListener("change", function () {
    activateExecutionPoint()
})


function sendData(event) {
    const form = document.getElementById("simulationForm")
    let errorConnection = document.getElementById("error-disconnected")
    event.preventDefault(); // Evitar que el formulario se envíe de la forma predeterminada

    const formData = new FormData(form)
    formData.set('mobilization', document.getElementById("mobilization").checked)

    fetch('http://' + ip + ':5000/submit', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
            else simulatingButtonsState()
            return response.json();
        })
        .then(data => {
            errorConnection.style.display = "none"
            console.log('Server Response:', data)
        })
        .catch(error => {
            errorConnection.style.display = "block"
            console.error('Error:', error)
        })
}

function simulatingButtonsState() {
    simulateButton.disabled = true
    simulateButton.innerText = "SIMULANDO..."

    stopButton.disabled = false
    stopButton.innerText = "PARAR"
}

function stoppedButtonsState() {
    simulateButton.disabled = false
    simulateButton.innerText = "SIMULAR"

    stopButton.disabled = true
    stopButton.innerText = "PARADO"
}

stopButton.addEventListener("click", function (event) {
    event.preventDefault()
    const data = { simulating: 'False' }
    let errorConnection = document.getElementById("error-disconnected")


    fetch('http://' + ip + ':5000/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok ' + response.statusText)
            else stoppedButtonsState()
            return response.json();
        })
        .then(data => {
            errorConnection.style.display = "none"
            console.log('Server Response:', data)
        })
        .catch(error => {
            errorConnection.style.display = "block"
            console.error('Error:', error)
        })
})

// Se añade al boton del formulario la validación y subida de datos cuando se haga click
simulateButton.addEventListener("click", function (event) {
    // Se obtienen los valores seleccionados de los select
    let movementSelected = movements.value
    let endFeelSelected = endfeels.value
    let executionPoint = range.value
    let dataError = 0

    let errorMovement = document.getElementById("error-movement")
    let errorEndFeel = document.getElementById("error-endfeel")
    let errorRange = document.getElementById("error-range")

    // Si en el select de movimientos no hay ningun valor elegido...
    if (movementSelected === "disabled") {
        errorMovement.style.display = "block"
        event.preventDefault()
        dataError = 1
    } else { // Si hay valor elegido...
        errorMovement.style.display = "none"
    }

    // Si en el select de endfeel no hay ningun valor elegido...
    if (endFeelSelected === "disabled") {
        errorEndFeel.style.display = "block"
        event.preventDefault()
        dataError = 1
    } else { // Si hay valor elegido...
        errorEndFeel.style.display = "none"
    }

    // Si el valor de range executionPoint es 0...
    if (executionPoint == 0 && range.disabled == false) {
        errorRange.style.display = "block"
        event.preventDefault()
        dataError = 1
    } else { // Si el cualquier otro valor
        errorRange.style.display = "none"
    }

    if (dataError === 0) {
        sendData(event)
    }
})

document.addEventListener('DOMContentLoaded', function () {
    let errorConnection = document.getElementById("error-disconnected")

    fetch('http://' + ip + ':5000/simulating')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Server Response:', data)
            errorConnection.style.display = "none"
            if (data['simulating'] == "true") simulatingButtonsState()
            else stoppedButtonsState()

            if (data['articulation'] !== null && data['movement'] !== null && data['endfeel'] !== null && data['mobilization'] !== null && data['executionPoint'] !== null) {
                articulations.value = data['articulation']
                movements.value = data['movement']
                endfeels.value = data['endfeel']
                mobilization.checked = data['mobilization'] == "true" ? true : false
                activateExecutionPoint()
                range.value = data['executionPoint']
                range.nextElementSibling.querySelector('output').value = data['executionPoint']
            }
        })
        .catch(error => {
            errorConnection.style.display = "block"
            console.error('Error:', error);
        });
})