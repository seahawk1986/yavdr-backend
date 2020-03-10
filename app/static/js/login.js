"use strict";

var token_data = null;
var modal_login_instance;      // the login dialog
var modal_connection_instance; // the connection lost dialog (TODO)

function logout() {
    console.log("called logout")
    token_data = null;
    modal_login_instance.open();
}

function handleHTTPErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response.json();
}

async function authenticated_http_request(url, method="GET", request_data={}) {
    if (token_data === null) throw "token is null";
    const myHeaders = new Headers();
    myHeaders.append("accept", "application/json");
    myHeaders.append("Authorization", `Bearer ${token_data.access_token}`)
    let data = fetch(url,
        {
            method: method,
            mode: 'cors',
            cache: 'default',
            headers: myHeaders,
            body: (method.toUpperCase() == "GET") ? null : JSON.stringify(request_data),
        }
    ).then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json();
        }
    ).catch(err => {
            console.error("http request failed:", err);
            throw err;
        })
    console.log("end of authenticated http request")
    return data;
}

document.addEventListener('DOMContentLoaded', function () {
    M.AutoInit();

    var elems = document.querySelectorAll('#modal-login');
    var options = {
        "dismissible": false,
    }
    var instances = M.Modal.init(elems, options);

    modal_login_instance = M.Modal.getInstance(document.getElementById("modal-login"));
    const loginForm = document.getElementById('login_form');
    const login_msg = document.getElementById('login_msg');
    const login_progress = document.getElementById('login_progress');
    const login_btn = document.getElementById('login_btn');

    if (token_data === null) {
        modal_login_instance.open();
        const login_username = document.getElementById('login_username');
        login_username.focus();
    }
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        // console.log("Login button clicked...")
        login_btn.disabled = true;
        login_msg.textContent = "";
        login_progress.innerHTML = '<div class="progress"><div class="indeterminate" style="width: 0%"></div></div>'

        const myHeaders = new Headers();
        myHeaders.append("accept", "application/json");

        const formData = new FormData(this);

        // TODO: remove this debug output
        // for (var [key, value] of formData.entries()) { 
        // 	console.log(key, value);
        // }

        fetch("/token", {
            method: "post",
            mode: 'cors',
            cache: 'default',
            headers: myHeaders,
            body: formData,
        })
            .then(
                (response) => {
                    // console.log("got response:", response);
                    return response.json();
                })
            .then(
                (data) => {
                    // console.log("got data:", data);
                    token_data = data;
                    document.getElementById("login_password").value = '';
                    authenticated_http_request("/users/me").then((request_data) => {
                        console.log("got data:", request_data);
                        login_msg.textContent = "";
                        login_progress.innerHTML = "";
                        const greeting = document.getElementById("greeting");
                        greeting.textContent = `Hallo, ${request_data.username}`;
                        console.log("set greeting");
                        modal_login_instance.close();
                    }).catch(err => {
                        console.error("login failed:", err);
                        login_progress.innerHTML = "";
                        login_msg.innerHTML = "<h6>Invalid username or password.</h6>";
                    });
                    authenticated_http_request("/system/status").then(request_data => {
                        const status_div = document.getElementById("system_status");
                        let temp_data = '<div class="section">';
                        for (let tmp_data of request_data.temperatures.coretemp) {
                            temp_data += `
                            <div>
                                <label for='${tmp_data.label}'>${tmp_data.label}<i class="material-icons prefix">memory</i></label>
                                <meter id='${tmp_data.label}' title="°C"  value="${tmp_data.current}" max="${tmp_data.critical}" min="0">${tmp_data.current}</meter>
                                ${tmp_data.current} °C
                                <br>
                            </div>
                            `
                        };
                        if (request_data.temperatures.nvidia_temp) {
                            console.log(request_data.temperatures.nvidia_temp);
                            temp_data += `
                            <div>
                                <label for='nvidia_gpu'>NVidia GPU <i class="material-icons prefix">memory</i></label>
                                <meter id='nvidia_gpu' title="°C" value="${request_data.temperatures.nvidia_temp}" max="100" min="0">${request_data.temperatures.nvidia_temp}</meter>
                                ${request_data.temperatures.nvidia_temp} °C
                            </div>
                            `;
                        };
                        temp_data += "</div>";
                        status_div.innerHTML = temp_data;
                    }).catch(err => {
                        console.error("could not retrieve /system/status", err);
                    })
                    login_btn.disabled = false;
                }
            )
            .catch((err) => {
                console.error("Aquiring token failed:", err);
                login_msg.textContent = "Invalid username or password.";
                login_btn.disabled = false;
            })
            
    })
});