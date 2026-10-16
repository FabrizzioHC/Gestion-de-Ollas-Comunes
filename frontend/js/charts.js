// charts.js - funciones para renderizar gráficos en el frontend
/* global Chart, api */

async function initProfileCharts(user) {
    if (!user) return;
    const container = document.getElementById('chartsContainer') || document.getElementById('profileChartsContainer');
    if (!container) return;
    // limpiar
    container.innerHTML = '';

    try {
        if (user.role === 'admin') {
            // crear canvases
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-4"><canvas id="chartOllasTop"></canvas></div>
                    <div class="col-md-6 mb-4"><canvas id="chartRecursos"></canvas></div>
                    <div class="col-md-12 mb-4"><canvas id="chartDistritos"></canvas></div>
                </div>
            `;
            await renderAdminCharts();
        } else if (user.role === 'olla_comun') {
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-4"><canvas id="chartOllaRecursos"></canvas></div>
                    <div class="col-md-6 mb-4"><canvas id="chartOllaDonantes"></canvas></div>
                    <div class="col-md-12 mb-4"><canvas id="chartOllaHist"></canvas></div>
                </div>
            `;
            await renderOllaCharts(user);
        } else if (user.role === 'donador') {
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-4"><canvas id="chartDonadorOllas"></canvas></div>
                    <div class="col-md-6 mb-4"><canvas id="chartDonadorRecursos"></canvas></div>
                    <div class="col-md-12 mb-4"><canvas id="chartDonadorDistritos"></canvas></div>
                </div>
            `;
            await renderDonadorCharts(user);
        }
    } catch (err) {
        console.error('Error inicializando gráficos:', err);
    }
}

// Render charts on the main Dashboard (home) per role
async function initDashboardCharts(user) {
    const container = document.getElementById('dashboardChartsContainer');
    if (!container) return;
    container.innerHTML = '';
    try {
        if (user.role === 'admin') {
            // use same ids as profile charts so renderAdminCharts finds them
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-4"><canvas id="chartOllasTop"></canvas></div>
                    <div class="col-md-6 mb-4"><canvas id="chartRecursos"></canvas></div>
                    <div class="col-md-12 mb-4"><canvas id="chartDistritos"></canvas></div>
                </div>
            `;
            await renderAdminCharts();
        } else if (user.role === 'olla_comun') {
            // use same ids as profile view
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-4"><canvas id="chartOllaRecursos"></canvas></div>
                    <div class="col-md-6 mb-4"><canvas id="chartOllaDonantes"></canvas></div>
                    <div class="col-md-12 mb-4"><canvas id="chartOllaHist"></canvas></div>
                </div>
            `;
            await renderOllaCharts(user);
        } else if (user.role === 'donador') {
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-4"><canvas id="chartDonadorOllas"></canvas></div>
                    <div class="col-md-6 mb-4"><canvas id="chartDonadorRecursos"></canvas></div>
                    <div class="col-md-12 mb-4"><canvas id="chartDonadorDistritos"></canvas></div>
                </div>
            `;
            await renderDonadorCharts(user);
        }
    } catch (err) {
        console.error('Error inicializando dashboard charts:', err);
    }
}

window.appCharts = { initProfileCharts, initDashboardCharts };

function sumBy(arr, keyFn) {
    const map = new Map();
    arr.forEach(item => {
        const key = keyFn(item);
        map.set(key, (map.get(key) || 0) + (Number(item.cantidad) || 0) );
    });
    return Array.from(map.entries()).map(([k,v]) => ({k,v}));
}

async function renderAdminCharts() {
    // obtener datos
    const [ollas, donaciones] = await Promise.all([api.listOllas(), api.listDonaciones()]);

    // Top ollas por recursos (sum cantidad)
    const byOlla = new Map();
    donaciones.forEach(d => {
        const id = d.olla_comun_id || 'Sin Olla';
        byOlla.set(id, (byOlla.get(id) || 0) + Number(d.cantidad || 0));
    });
    const ollaLabels = [];
    const ollaValues = [];
    Array.from(byOlla.entries()).sort((a,b)=>b[1]-a[1]).slice(0,6).forEach(([id,val]) => {
        const o = ollas.find(x=>x.id==id);
        ollaLabels.push(o ? o.nombre : (id === 'Sin Olla' ? 'Sin Olla' : `Olla #${id}`));
        ollaValues.push(val);
    });
    const ctxOllas = document.getElementById('chartOllasTop').getContext('2d');
    new Chart(ctxOllas, { type: 'bar', data: { labels: ollaLabels, datasets: [{ label: 'Total recursos (suma cantidad)', data: ollaValues, backgroundColor: '#4dc9f6' }] }, options: { responsive:true } });

    // Recursos favoritos
    const byRecurso = {};
    donaciones.forEach(d => { const r = d.tipo_recurso || 'Otro'; byRecurso[r] = (byRecurso[r]||0)+Number(d.cantidad||0); });
    const recursoLabels = Object.keys(byRecurso);
    const recursoValues = recursoLabels.map(l=>byRecurso[l]);
    const ctxRec = document.getElementById('chartRecursos').getContext('2d');
    new Chart(ctxRec, { type: 'pie', data: { labels: recursoLabels, datasets: [{ data: recursoValues, backgroundColor: ['#36a2eb','#ff6384','#ffcd56','#4bc0c0','#9966ff'] }] }, options: { responsive:true } });

    // Distritos con más ollas (heurística: tomar último segmento de direccion separado por comma/-)
    const districtCounts = {};
    ollas.forEach(o=>{
        let d = (o.direccion||'').split(',').pop().split('-').pop().trim();
        if (!d) d = 'Desconocido';
        districtCounts[d] = (districtCounts[d]||0)+1;
    });
    const distLabels = Object.keys(districtCounts).slice(0,10);
    const distValues = distLabels.map(l=>districtCounts[l]);
    const ctxDist = document.getElementById('chartDistritos').getContext('2d');
    new Chart(ctxDist, { type: 'bar', data: { labels: distLabels, datasets: [{ label: 'Ollas por distrito', data: distValues, backgroundColor: '#6a5acd' }] }, options: { responsive:true } });
}

async function renderOllaCharts(user) {
    // para olla_comun, backend retorna solo las donaciones de su olla
    const donaciones = await api.listDonaciones();
    // recursos activos
    const recursos = {};
    donaciones.forEach(d=>{ const r=d.tipo_recurso||'Otro'; recursos[r]=(recursos[r]||0)+Number(d.cantidad||0); });
    const labelsRec = Object.keys(recursos);
    const dataRec = labelsRec.map(l=>recursos[l]);
    const ctxRecElement = document.getElementById('chartOllaRecursos');
    if (ctxRecElement) {
        const ctxRec = ctxRecElement.getContext('2d');
        new Chart(ctxRec, { type:'doughnut', data:{ labels: labelsRec, datasets:[{ data: dataRec, backgroundColor:['#36a2eb','#ff6384','#ffcd56','#4bc0c0'] }]}, options:{ responsive:true }});
    }

    // mayores donantes - usar lista pública para mapear nombres
    const publicDon = await api.listPublicDonaciones();
    // intentar determinar la olla id asociada a este usuario si es posible
    const allOllas = await api.listOllas();
    const myOlla = allOllas.find(o => o.usuario_id == user.id) || allOllas[0];
    const myOllaId = myOlla ? myOlla.id : null;
    const donors = {};
    publicDon.filter(d => d.destino && (myOllaId == null || (myOlla && d.destino.includes(myOlla.nombre)))).forEach(d => {
        donors[d.donante] = (donors[d.donante] || 0) + 1;
    });
    const donorLabels = Object.keys(donors).slice(0, 6);
    const donorValues = donorLabels.map(l => donors[l]);
    const ctxDonElement = document.getElementById('chartOllaDonantes');
    if (ctxDonElement) {
        const ctxDon = ctxDonElement.getContext('2d');
        new Chart(ctxDon, { type:'bar', data:{ labels: donorLabels, datasets:[{ label:'Número de donaciones', data: donorValues, backgroundColor:'#20c997' }]}, options:{ responsive:true }});
    }

    // historial de donaciones (por mes)
    const byMonth = {};
    donaciones.forEach(d=>{
        const dt = new Date(d.fecha_creacion || d.fecha || Date.now());
        const key = dt.getFullYear() + '-' + String(dt.getMonth()+1).padStart(2,'0');
        byMonth[key] = (byMonth[key]||0) + Number(d.cantidad||0);
    });
    const histLabels = Object.keys(byMonth).sort();
    const histValues = histLabels.map(l=>byMonth[l]);
    const ctxHist = document.getElementById('chartOllaHist').getContext('2d');
    new Chart(ctxHist, { type:'line', data:{ labels: histLabels, datasets:[{ label:'Cantidad donada', data: histValues, borderColor:'#007bff', fill:false }]}, options:{ responsive:true }});
}

async function renderDonadorCharts(user) {
    const donaciones = await api.listDonaciones();
    const ollas = await api.listOllas();

    // ollas a las que ha donado
    const byOlla = {};
    donaciones.forEach(d=>{ const id = d.olla_comun_id || 'Sin Olla'; byOlla[id] = (byOlla[id]||0) + Number(d.cantidad||0); });
    const ollaLabels = Object.keys(byOlla).map(id=>{ const o = ollas.find(x=>x.id==id); return o ? o.nombre : (id==='Sin Olla'?'Sin Olla':`Olla #${id}`); });
    const ollaValues = Object.keys(byOlla).map(id=>byOlla[id]);
    const ctxOllas = document.getElementById('chartDonadorOllas').getContext('2d');
    new Chart(ctxOllas,{ type:'bar', data:{ labels: ollaLabels, datasets:[{ label:'Total donado', data: ollaValues, backgroundColor:'#17a2b8' }]}, options:{ responsive:true }});

    // recursos donados
    const byRecurso = {};
    donaciones.forEach(d=>{ const r=d.tipo_recurso||'Otro'; byRecurso[r]=(byRecurso[r]||0)+Number(d.cantidad||0); });
    const recLabels = Object.keys(byRecurso);
    const recValues = recLabels.map(l=>byRecurso[l]);
    const ctxRec = document.getElementById('chartDonadorRecursos').getContext('2d');
    new Chart(ctxRec,{ type:'pie', data:{ labels: recLabels, datasets:[{ data: recValues, backgroundColor:['#ff6384','#36a2eb','#ffcd56','#4bc0c0'] }]}, options:{ responsive:true }});

    // distritos (heurística similar a admin)
    const districtCounts = {};
    ollas.forEach(o=>{ let d=(o.direccion||'').split(',').pop().split('-').pop().trim(); if(!d) d='Desconocido'; districtCounts[d]=(districtCounts[d]||0)+ (donaciones.some(dd=>dd.olla_comun_id==o.id)?1:0); });
    const distLabels = Object.keys(districtCounts).slice(0,8);
    const distValues = distLabels.map(l=>districtCounts[l]);
    const ctxDist = document.getElementById('chartDonadorDistritos').getContext('2d');
    new Chart(ctxDist,{ type:'bar', data:{ labels: distLabels, datasets:[{ label:'Distritos', data: distValues, backgroundColor:'#6f42c1' }]}, options:{ responsive:true }});
}

// window.appCharts already set above; nothing more to export here
