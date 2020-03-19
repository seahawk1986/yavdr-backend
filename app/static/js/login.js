"use strict";

var auth; // our Authorization instance

class Authorization {
    constructor() {
        // initialize the modal login dialog
        var elems = document.querySelectorAll('#modal-login');
        var options = {
            "dismissible": false,
        }
        var instances = M.Modal.init(elems, options);

        // set up variables
        this.token_data = null;
        this.intervals = [];
        this.sys_stat_timer;
        this.refresh_token_timer;
        this.modal_login_instance = M.Modal.getInstance(document.getElementById("modal-login"));
        this.loginForm = document.getElementById('login_form');
        this.login_msg = document.getElementById('login_msg');
        this.login_progress = document.getElementById('login_progress');
        this.login_btn = document.getElementById('login_btn');

        if (this.token_data === null) {
            this.modal_login_instance.open();
            const login_username = document.getElementById('login_username');
            login_username.focus();
        }
    }

    handleHTTPErrors(response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }

    logout() {
        console.log("called logout")
        this.token_data = null;
        this.modal_login_instance.open();
        clearInterval(this.sys_stat_timer);
        clearInterval(this.refresh_token_timer);
    }

    login(form) {
        this.login_btn.disabled = true;
        this.login_msg.textContent = "";
        this.login_progress.innerHTML = '<div class="progress"><div class="indeterminate" style="width: 0%"></div></div>'

        const myHeaders = new Headers();
        myHeaders.append("accept", "application/json");
        const formData = new FormData(form);


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
                    this.token_data = data;
                    document.getElementById("login_password").value = '';
                    this.authenticated_http_request("/users/me").then((request_data) => {
                        // console.log("got data:", request_data);
                        this.login_msg.textContent = "";
                        this.login_progress.innerHTML = "";
                        const greeting = document.getElementById("greeting");
                        greeting.textContent = `Hallo, ${request_data.username}`;
                        // console.log("set greeting");
                        this.modal_login_instance.close();
                    }).catch(err => {
                        console.error("login failed:", err);
                        this.login_progress.innerHTML = "";
                        this.login_msg.innerHTML = "<h6>Invalid username or password.</h6>";
                    });
                    update_sys_stats();
                    this.sys_stat_timer = setInterval(update_sys_stats, 5000);
                    this.login_btn.disabled = false;
                    update_recordings();
                    update_timers();
                    this.refresh_token_timer = setInterval(this.refresh_token, 60 * 1000 * 5); // get a refresh token every 5 minutes
                }
            )
            .catch((err) => {
                console.error("Aquiring token failed:", err);
                this.login_msg.textContent = "Invalid username or password.";
                this.login_btn.disabled = false;
            })
    }

    async refresh_token() {
        this.authenticated_http_request("/token/refresh")
        .then(data => {
            console.log("successfully got a new token.")
            this.access_token = data.access_token;
        }
        ).catch(err => console.error("could not retrieve access token"))
    }

    async authenticated_http_request(url, method = "GET", request_data = {}) {
        if (this.token_data === null) throw "token is null";
        const myHeaders = new Headers();
        myHeaders.append("accept", "application/json");
        myHeaders.append("Authorization", `Bearer ${this.token_data.access_token}`)
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
        // console.log("end of authenticated http request")
        return data;
    }
}

async function hit_key(key) {
    auth.authenticated_http_request("/hitkey", "POST", {"key": key})
    .then(data => {
        console.log("sent key", key);
    }).catch(err => console.error("sending", key, "failed:", err));
    
}

async function update_sys_stats() {
    auth.authenticated_http_request("/system/status").then(request_data => {
        const status_div = document.getElementById("system_status");
        let temp_data = '<div class="section">';
        for (let [i, v] of Object.entries(request_data.temperatures)) {
            temp_data += `<div class="section"><div class="row"><span class="col 12s valign-center"><h6><i class="material-icons">developer_board</i> ${i}</h6></span></div>`;
            v.forEach((t, n) => {
                let temp_name = (t.label) ? t.label : `Temp_${n}`
                temp_data += `
                    <div class="row">
                        <span class="col s2">${temp_name}</span>
                        <div class="col s2 meter">
                            <span style="width: ${t.current/115 * 100}%"></span>
                        </div>
                        <div class="col s1 right-align">${t.current.toFixed(1)} °C</div>
                        <br>
                    </div>
                    `;
            });
            temp_data += '</div>'
        };
        temp_data += "</div>";
        status_div.innerHTML = temp_data;

        const fans_div = document.getElementById("system_fans");
        temp_data = '';
        for (let [i, v] of Object.entries(request_data.fans)) {
            temp_data += `<div class="section"><div class="row"><span class="col 12s valign-center"><h6><i class="material-icons">toys</i> ${i}</h6></span></div>`;
            v.forEach((f, n) => {
                let fan_name = (f.label) ? f.label : `Fan_${n}`;
                temp_data += `
                    <div class="row">
                        <div class="col s1 m1">${fan_name}</div>
                        <div class="col s1 m1 right-align">${f.current}</div>
                        <div class="col s1 m1">RPM</div>
                    </div>
                    `;
            })
            temp_data += "</div>"
        }
        fans_div.innerHTML = temp_data;

        const disk_div = document.getElementById('system_hdd');
        temp_data = `
            <div class="row">
                <div class="col s2">Mountpoint</div>
                <div class="col s1">Device</div>
                <div class="col s1"><i class="material-icons">storage</i></div>
                <div class="col s5">Usage</div>
            </div>
        `;
        request_data.disk_usage.forEach((d, n) => {
            temp_data += `
                        <div class="row">
                            
                            <div class="col s2">${d.mountpoint}</div>
                            <span class="col s1">${d.device}</span>
                            <div class="col s1 meter">
                                <span style="width: ${d.percent}%"></span>
                            </div>
                            <div class="col s5">${d.used_human.value} ${d.used_human.unit}/${d.total_human.value} ${d.total_human.unit} (${d.free_human.value} ${d.free_human.unit} free)</div>
                        </div>
                        `
        });
        disk_div.innerHTML = temp_data;

        temp_data = `
        <div class="row">
            <i class="material-icons col s1">device_hub</i>
            <div class="col s2">${request_data.release.join(' ')}</div>
            <div class="col s2">Kernel: ${request_data.kernel}</div> 
        </div>
        `;
        const res_div = document.getElementById('system_resources');
        const m = request_data.memory_usage;
        const c = request_data.cpu_usage;
        const n_cpus = request_data.cpu_num;
        let i;
        for (i = 0; i < n_cpus; i++) {
            temp_data += `
                <div class="row">
                    <i class="material-icons prefix col s1">memory</i>
                    <span class="col s2">CPU ${i}</span>
                    <div class="col s1 meter">
                        <span style="width: ${c[i]/100}%"></span>
                    </div>
                    <div class="col s1">${c[i].toFixed(1)}%</div>
                </div>
            `;
        }
        temp_data += `
                    <div class="row">
                        <i class="material-icons prefix col s1">memory</i>
                        <span class="col s2">RAM</span>
                        <div class="col s1 meter">
                            <span style="width: ${m.percent}%"></span>
                        </div>
                        <div class="col s2">${m.used_human.value} ${m.used_human.unit}/${m.total_human.value} ${m.total_human.unit}</div>
                        <div class="col s2">${m.free_human.value} ${m.free_human.unit} free</div>
                    </div>
                    `;
        res_div.innerHTML = temp_data;
        auth.login_btn.disabled = false;
        })
        .catch(err => {
            console.error("could not retrieve /system/status", err);
        })    
}

async function update_recordings() {
    const update_recordings_btn = document.getElementById("update-recordings-btn");
    update_recordings_btn.disabled = true;
    auth.authenticated_http_request("/vdr/recordings")
    .then(data => {
        const recordings_ul = document.getElementById("vdr_recordings");
        let rec_html = `
        <li>
            <div class="row highlight">
                <div class="col s1">Seen</div>
                <div class="col s2 right-align">Recording Start Date</div>
                <div class="col s1 right-align">Duration (HH:MM:SS)</div>
                <div class="col s7">Path</div>
            </div>
        </li>`;
        data.sort((a, b) => b.Start - a.Start) // sort by date, newest first
        .forEach((r, i) => {
            let start_date = new Date(r.Start * 1000).toLocaleString(undefined, {
                "year": "numeric",
                "month": "2-digit",
                "day": "2-digit",
                "hour": "2-digit",
                "minute": "2-digit"
            });
            let duration_str = (
                Math.floor((r.LengthInSeconds / 3600)).toString().padStart(2, "0") + ":" + 
                Math.floor((r.LengthInSeconds % 3600) / 60).toString().padStart(2, "0") + ":" +
                Math.floor((r.LengthInSeconds % 3600) % 60).toString().padStart(2, "0")
            );
            let is_new = (r.IsNew) ? `<i class="material-icons col s1">fiber_new</i>` : `<i class="material-icons">note</i>`;
            rec_html += `
            <li>
                <div class="row highlight">
                    <div class="col s1"><i class="material-icons">${(r.IsNew) ? "fiber_new" : "note"}</i></div>
                    <div class="col s2 right-align">${start_date}</div>
                    <div class="col s1 right-align">${duration_str}</div>
                    <div class="col s7">${r.FullName}</div>
                </div>
            </li>`
            
        });
        recordings_ul.innerHTML = rec_html;
        update_recordings_btn.disabled = false;
    })
    .catch(err => {
        console.error("could not get recordings:", err)
        update_recordings_btn.disabled = false;
    })
}


async function update_timers() {
    const update_timer_btn = document.getElementById("update-timers-btn");
    update_timer_btn.disabled = true;
    auth.authenticated_http_request("/vdr/timers")
    .then(data => {
        const timer_ul = document.getElementById("vdr_timers");
        let timer_html = `
        <li>
            <div class="row">
                <div class="col s1">State</div>
                <div class="col s2">Date</div>
                <div class="col s2">Time</div>
                <div class="col s7">Name</div>
            </div>
        </li>
        `;
        data.forEach((t, i) => {
            let start = t.start.toString();
            let stop = t.stop.toString();
            timer_html += `
            <li>
                <div class="row">
                    <div class="col s1"><i class="material-icons">${(t.status != 0) ? "fiber_manual_record" : "not_interested"}</i></div>
                    <div class="col s2">${t.day}</div>
                    <div class="col s2">${start.slice(0,2) + ":" + start.slice(2,4)} - ${stop.slice(0,2) + ":" + stop.slice(2,4)}</div>
                    <div class="col s7">${t.filename}</div>
                </div>
            </li>`
            
        });
        timer_ul.innerHTML = timer_html;
        update_timer_btn.disabled = false;
    })
    .catch(err => {
        console.error("could not get timers:", err)
        update_timer_btn.disabled = false;
    })
}

document.addEventListener('DOMContentLoaded', function () {
    M.AutoInit();
    auth = new Authorization();
    let elems = document.querySelectorAll('.sidenav');
    let instances = M.Sidenav.init(elems,
        {
            "edge": "left",
        }
    );

    // wire up login button of modal login dialogue
    auth.loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        auth.login(this);
    })
});