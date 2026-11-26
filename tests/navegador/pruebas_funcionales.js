// Pruebas funcionales del dashboard en el navegador (Actividad 3.3).
//
// Requisitos: Node.js y Playwright (npm install playwright && npx playwright install chromium).
// 1. En una terminal, desde la raíz del repositorio: python -m streamlit run dashboard/app.py
// 2. En otra:  node tests/navegador/pruebas_funcionales.js
//    (opcional: URL=http://localhost:8501 OUT=carpeta_de_capturas)
// Imprime PASA o FALLA por caso y guarda resultados.json y las capturas en OUT.
// Usa la contraseña por defecto «admin»; si la cambió, cambie la función login.
const { chromium } = require('playwright');
const URL = process.env.URL || 'http://localhost:8501';
const OUT = process.env.OUT || 'capturas_pruebas';
require('fs').mkdirSync(OUT, {recursive:true});
const res = [];
function rec(id, nombre, ok, detalle, ms){ res.push({id, nombre, ok, detalle, ms}); console.log(`${ok?'PASA':'FALLA'} ${id} ${nombre} | ${detalle} | ${ms} ms`); }
async function horaSim(pg){ const t = await pg.getByText(/Hora simulada:/).first().innerText(); return t.match(/(\d\d\/\d\d\/\d{4} \d\d:\d\d)/)[1]; }
async function franja(pg){ return (await pg.getByText(/Cuenca:/).first().innerText()).trim(); }
async function esperarHora(pg, h, ms=20000){ const t0=Date.now(); while(Date.now()-t0<ms){ try{ if(await horaSim(pg)===h) return true; }catch(e){} await pg.waitForTimeout(250);} return false; }
async function irA(pg, fecha, hh){
  const [dd,mm,yy]=fecha.split('/');
  const day = pg.getByRole('spinbutton',{name:'day, Fecha de inicio'}); await day.click(); await pg.keyboard.type(dd+mm+yy); await pg.keyboard.press('Tab'); await pg.waitForTimeout(2000);
  await pg.waitForTimeout(500);
  const sel = pg.getByRole('combobox',{name:'Hora de inicio'}); await sel.click(); await pg.waitForTimeout(600); await sel.fill(hh); await pg.waitForTimeout(600);
  const op = pg.getByRole('option',{name:hh,exact:true}); if (await op.count()) await op.first().click(); else await pg.keyboard.press('Enter');
  await pg.waitForTimeout(500);
  await pg.getByRole('button',{name:'Ir a esa fecha'}).click();
}
async function login(pg, clave){ await pg.getByLabel('Contraseña').fill(clave); await pg.getByRole('button',{name:'Entrar'}).click(); }
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({viewport:{width:1400,height:900}});
  const pg = await ctx.newPage(); const errores=[];
  pg.on('console', m => { if (m.type()==='error') errores.push(m.text()); });
  pg.on('pageerror', e => errores.push(String(e)));
  let t0=Date.now();
  await pg.goto(URL); await pg.getByLabel('Contraseña').waitFor({timeout:90000});
  rec('CP-01','Carga de la pantalla de acceso', true, 'Formulario de contraseña visible', Date.now()-t0);
  await pg.screenshot({path:`${OUT}/01_acceso.png`});
  t0=Date.now(); await login(pg,'clave-equivocada');
  let ok = await pg.getByText('Contraseña incorrecta.').waitFor({timeout:15000}).then(()=>true).catch(()=>false);
  rec('CP-02','Acceso con contraseña incorrecta', ok, ok?'Muestra «Contraseña incorrecta.» y no entra':'No mostró el error', Date.now()-t0);
  t0=Date.now(); await login(pg,'admin');
  ok = await pg.getByText(/Cuenca:/).first().waitFor({timeout:120000}).then(()=>true).catch(()=>false);
  rec('CP-03','Acceso con contraseña correcta', ok, ok?'Entra al panel general':'No entró', Date.now()-t0);
  await pg.waitForTimeout(1500);
  let h = await horaSim(pg); let fr = await franja(pg);
  const tarjetas = await pg.getByText(/Rango probable:/).count();
  ok = h==='13/11/2024 00:00' && /NORMAL/.test(fr) && tarjetas>=2;
  rec('CP-04','Panel general inicial', ok, `Hora ${h}; franja «${fr}»; ${tarjetas} tarjetas de estación con pronóstico y rango`, 0);
  await pg.screenshot({path:`${OUT}/04_panel_inicial.png`, fullPage:true});

  t0=Date.now(); await pg.getByRole('button',{name:'+1 h ⏭'}).click(); let a = await esperarHora(pg,'13/11/2024 01:00');
  await pg.getByRole('button',{name:'⏮ −1 h'}).click(); let c = await esperarHora(pg,'13/11/2024 00:00');
  rec('CP-05','Avance y retroceso de una hora', a&&c, `+1 h → 01:00 (${a}); −1 h → 00:00 (${c})`, Date.now()-t0);

  t0=Date.now(); await irA(pg,'13/11/2024','07:00'); ok = await esperarHora(pg,'13/11/2024 07:00'); fr=await franja(pg);
  rec('CP-06','Ir a una fecha y hora', ok && /NARANJA/.test(fr), `Hora ${await horaSim(pg)}; franja «${fr}» (esperado NARANJA, Informe 3.2)`, Date.now()-t0);
  await pg.screenshot({path:`${OUT}/06_naranja.png`, fullPage:true});
  await pg.getByRole('button',{name:'+1 h ⏭'}).click(); await esperarHora(pg,'13/11/2024 08:00'); await pg.waitForTimeout(800); fr=await franja(pg);
  rec('CP-07','Escalamiento a rojo', /ROJO/.test(fr), `08:00 → franja «${fr}» (esperado ROJO)`, 0);

  // Play
  t0=Date.now(); await pg.getByRole('button',{name:'▶ Play'}).click(); await pg.waitForTimeout(7000);
  const hp = await horaSim(pg); await pg.getByRole('button',{name:'⏸ Pausa'}).click(); await pg.waitForTimeout(1500);
  const h1 = await horaSim(pg); await pg.waitForTimeout(4000); const h2 = await horaSim(pg);
  const avanz = (new Date(hp.replace(/(\d\d)\/(\d\d)\/(\d{4})/,'$3-$2-$1')) - new Date('2024-11-13T08:00'))/3.6e6;
  rec('CP-08','Play y Pausa', avanz>=2 && h1===h2, `En ~7 s avanzó ${avanz} h (velocidad 1 h cada 2 s); en pausa se mantiene (${h1} = ${h2})`, Date.now()-t0);

  // Velocidad 24
  t0=Date.now();
  const slider = pg.locator('[data-testid="stSidebar"]').getByRole('slider').first(); await slider.focus(); await slider.press('End'); await pg.waitForTimeout(1200);
  const antes = await horaSim(pg); await pg.getByRole('button',{name:'▶ Play'}).click(); await pg.waitForTimeout(4500);
  await pg.getByRole('button',{name:'⏸ Pausa'}).click(); await pg.waitForTimeout(1200); const despues = await horaSim(pg);
  const dif = (new Date(despues.replace(/(\d\d)\/(\d\d)\/(\d{4})/,'$3-$2-$1')) - new Date(antes.replace(/(\d\d)\/(\d\d)\/(\d{4})/,'$3-$2-$1')))/3.6e6;
  rec('CP-09','Velocidad de 24 h por paso', dif>=24 && dif%24===0, `De ${antes} a ${despues}: ${dif} h`, Date.now()-t0);
  await slider.focus(); await slider.press('Home'); await pg.waitForTimeout(800);

  // Umbrales
  t0=Date.now(); await irA(pg,'13/11/2024','00:00'); await esperarHora(pg,'13/11/2024 00:00');
  await pg.locator('[data-testid="stSidebar"] [data-testid="stExpander"]').first().locator('summary').click(); await pg.waitForTimeout(500);
  const am = pg.locator('[data-testid="stSidebar"]').getByLabel('Amarillo (m sobre la base)').first();
  await am.fill('0.10'); await am.press('Enter'); await pg.waitForTimeout(2500); fr=await franja(pg);
  rec('CP-10','Cambio de umbral recalcula el aviso', /AMARILLO/.test(fr), `Amarillo La Lindosa 0,48 → 0,10 m con 0,16 m sobre la base: franja «${fr}»`, Date.now()-t0);
  await pg.screenshot({path:`${OUT}/10_umbral.png`, fullPage:true});
  t0=Date.now(); const na = pg.locator('[data-testid="stSidebar"]').getByLabel('Naranja (m sobre la base)').first();
  await na.fill('0.08'); await na.press('Enter'); await pg.waitForTimeout(1500);
  ok = await pg.getByText('El umbral naranja debería ser mayor que el amarillo.').isVisible();
  rec('CP-11','Validación naranja menor que amarillo', ok, ok?'Muestra la advertencia':'Sin advertencia', Date.now()-t0);
  t0=Date.now(); await pg.getByRole('button',{name:'Restablecer valores provisionales'}).click(); await pg.waitForTimeout(2500); fr=await franja(pg);
  const vam = await pg.locator('[data-testid="stSidebar"]').getByLabel('Amarillo (m sobre la base)').first().inputValue().catch(()=>'?');
  rec('CP-12','Restablecer valores provisionales', /NORMAL/.test(fr) && vam==='0.48', `Franja «${fr}»; amarillo vuelve a ${vam}`, Date.now()-t0);

  // Sin dato
  t0=Date.now(); await irA(pg,'03/06/2025','00:00'); await esperarHora(pg,'03/06/2025 00:00'); await pg.waitForTimeout(800); fr=await franja(pg);
  const gris = await pg.getByText('○ Sin dato').count();
  rec('CP-13','Estación sin datos (falla de 3 h)', /SIN DATO/.test(fr) && gris>0, `03/06/2025 00:00: franja «${fr}»; etiqueta ○ Sin dato visible`, Date.now()-t0);
  await pg.screenshot({path:`${OUT}/13_sin_dato.png`, fullPage:true});

  // Detalle
  await irA(pg,'13/11/2024','07:00'); await esperarHora(pg,'13/11/2024 07:00');
  t0=Date.now(); await pg.getByRole('radiogroup',{name:'Estación'}).getByText('Los Micos').click();
  await pg.getByRole('radiogroup',{name:'Ventana'}).getByText('30 días').click(); await pg.waitForTimeout(2500);
  const graf = await pg.locator('.js-plotly-plot').count(); const leyenda = await pg.getByText('Pronóstico a 6 h').count();
  rec('CP-14','Detalle de estación (Los Micos, 30 días)', graf>=1, `${graf} gráfica Plotly visible`, Date.now()-t0);
  await pg.screenshot({path:`${OUT}/14_detalle.png`, fullPage:true});
  await pg.getByRole('radiogroup',{name:'Ventana'}).getByText('72 horas').click(); await pg.getByRole('radiogroup',{name:'Estación'}).getByText('La Lindosa').click(); await pg.waitForTimeout(1500);

  // Bitácora
  t0=Date.now(); await pg.getByRole('tab',{name:/Bitácora/}).click(); await pg.waitForTimeout(2000);
  const tabla = await pg.locator('[data-testid="stDataFrame"]').count();
  await pg.getByLabel('Mostrar los últimos').getByText('365 días').click(); await pg.waitForTimeout(1500);
  await pg.getByText('Ocultar fallas de datos').click(); await pg.waitForTimeout(1500);
  rec('CP-15','Bitácora de avisos', tabla>=1, `Tabla visible; filtros de 365 días y «Ocultar fallas de datos» funcionan sin error`, Date.now()-t0);
  await pg.screenshot({path:`${OUT}/15_bitacora.png`, fullPage:true});

  // Modelo
  t0=Date.now(); await pg.getByRole('tab',{name:/Modelo y umbrales/}).click(); await pg.waitForTimeout(1500);
  ok = await pg.getByText('Desempeño en 2025 a 6 h').isVisible() && await pg.getByText('Cómo se activa un aviso').isVisible();
  rec('CP-16','Vista «Modelo y umbrales»', ok, 'Desempeño 2025, niveles, umbrales en uso y reglas visibles', Date.now()-t0);

  // Fin de la serie
  t0=Date.now(); await irA(pg,'31/12/2025','20:00'); await esperarHora(pg,'31/12/2025 20:00');
  await pg.getByRole('button',{name:'▶ Play'}).click(); await pg.waitForTimeout(6000);
  const fin = await horaSim(pg); const playVis = await pg.getByRole('button',{name:'▶ Play'}).isVisible();
  rec('CP-17','La simulación se detiene al final de la serie', playVis, `Se detuvo en ${fin}; el botón vuelve a ▶ Play`, Date.now()-t0);

  // coma decimal en gráficas
  await pg.getByRole('tab',{name:/Detalle/}).click(); await pg.waitForTimeout(1500);
  const ticks = await pg.locator('.js-plotly-plot .ytick text').allTextContents();
  const punto = ticks.some(x=>/\d\.\d/.test(x));
  rec('CP-18','Coma decimal en los ejes de las gráficas (RNF-14)', !punto, `Etiquetas del eje Y: ${ticks.slice(0,6).join(' ')}`, 0);

  // Cerrar sesión
  t0=Date.now(); await pg.getByRole('button',{name:'Cerrar sesión'}).click();
  ok = await pg.getByLabel('Contraseña').waitFor({timeout:15000}).then(()=>true).catch(()=>false);
  rec('CP-19','Cerrar sesión', ok, ok?'Vuelve a la pantalla de acceso':'No volvió', Date.now()-t0);


  // ---- Casos agregados para verificar los ajustes de la Actividad 3.3
  t0=Date.now(); await pg.getByLabel('Contraseña').fill('admin'); await pg.getByRole('button',{name:'Entrar'}).click();
  await pg.getByText(/Cuenca:/).first().waitFor({timeout:60000}); await pg.waitForTimeout(1000);
  await irA(pg,'14/11/2024','00:00'); await esperarHora(pg,'14/11/2024 00:00');
  await pg.getByRole('button',{name:'▶ Play'}).click(); await pg.waitForTimeout(5000); await pg.getByRole('button',{name:'⏸ Pausa'}).click(); await pg.waitForTimeout(1500);
  const hs = await horaSim(pg); const selv = await pg.getByRole('combobox',{name:'Hora de inicio'}).inputValue();
  rec('CP-22','El selector de fecha sigue a la hora simulada', hs.endsWith(selv), `Tras Play y Pausa: hora simulada ${hs}; selector ${selv}`, Date.now()-t0);
  t0=Date.now();
  const histSum = pg.locator('[data-testid="stSidebar"] [data-testid="stExpander"]').filter({hasText:'Historial de cambios'}).locator('summary');
  const nAntes = parseInt((await histSum.innerText()).match(/\((\d+)\)/)[1]);
  await pg.getByLabel('Motivo del cambio (opcional)').fill('Prueba funcional 3.3'); await pg.getByLabel('Motivo del cambio (opcional)').press('Enter'); await pg.waitForTimeout(800);
  await pg.locator('[data-testid="stSidebar"] [data-testid="stExpander"]').filter({hasText:'Los Micos'}).locator('summary').click(); await pg.waitForTimeout(400);
  const nam = pg.locator('[data-testid="stSidebar"]').getByLabel('Naranja (m sobre la base)').nth(1); await nam.fill('0.70'); await nam.press('Enter'); await pg.waitForTimeout(2000);
  const hist = await pg.locator('[data-testid="stSidebar"] [data-testid="stExpander"]').filter({hasText:'Historial de cambios'}).locator('summary').innerText();
  const nDesp = parseInt(hist.match(/\((\d+)\)/)[1]);
  rec('CP-23','Historial de cambios de umbrales (RF-24)', nDesp===nAntes+1, `Cambio naranja Los Micos 0,68 → 0,70 con motivo: el historial pasa de ${nAntes} a ${nDesp} registros`, Date.now()-t0);
  await pg.locator('[data-testid="stSidebar"] [data-testid="stExpander"]').filter({hasText:'Historial de cambios'}).locator('summary').click(); await pg.waitForTimeout(800);
  await pg.locator('[data-testid="stSidebar"]').screenshot({path:`${OUT}/23_historial.png`});
  t0=Date.now(); await pg.getByRole('button',{name:'Cerrar sesión'}).click(); await pg.getByLabel('Contraseña').fill('admin'); await pg.getByRole('button',{name:'Entrar'}).click();
  await pg.getByText(/Cuenca:/).first().waitFor({timeout:60000}); await pg.waitForTimeout(800);
  const nam2 = await pg.locator('[data-testid="stSidebar"]').getByLabel('Naranja (m sobre la base)').nth(1).inputValue();
  rec('CP-24','Los umbrales en uso se conservan al volver a entrar', nam2==='0.70', `Casilla naranja de Los Micos tras salir y entrar: ${nam2}`, Date.now()-t0);
  t0=Date.now(); await pg.getByRole('tab',{name:/Detalle/}).click(); await pg.waitForTimeout(800);
  const [dl] = await Promise.all([pg.waitForEvent('download',{timeout:20000}), pg.getByRole('button',{name:/Descargar datos, pronósticos y avisos/}).click()]);
  const ruta = `${OUT}/${dl.suggestedFilename()}`; await dl.saveAs(ruta); const csv = require('fs').readFileSync(ruta,'utf8').split('\n');
  rec('CP-25','Descarga de pronósticos con versión del modelo (RF-12)', csv[0].includes('version_modelo') && csv.length>70, `${dl.suggestedFilename()}: ${csv.length-2} filas; columnas: ${csv[0].replace(/^\uFEFF/,'').split(',').length}`, Date.now()-t0);

  // Móvil 360 px
  const m = await b.newContext({viewport:{width:360,height:780}, deviceScaleFactor:2, isMobile:true, hasTouch:true});
  const mp = await m.newPage(); await mp.goto(URL); await mp.getByLabel('Contraseña').waitFor({timeout:90000}); await login(mp,'admin');
  await mp.getByText(/Cuenca:/).first().waitFor({timeout:120000}); await mp.waitForTimeout(2000);
  const sw = await mp.evaluate(()=>document.documentElement.scrollWidth);
  const anchoMain = await mp.evaluate(()=>{const e=document.querySelector('[data-testid="stMain"]'); return e? e.scrollWidth: -1;});
  await mp.screenshot({path:`${OUT}/20_movil_panel.png`, fullPage:true});
  rec('CP-20','Legible en celular de 360 px (RNF-07)', sw<=360, `Ancho del documento ${sw} px; contenido principal ${anchoMain} px`, 0);

  rec('CP-21','Sin errores en la consola del navegador', errores.length===0, errores.length? errores.slice(0,3).join(' / ') : 'Ningún error registrado', 0);
  require('fs').writeFileSync(`${OUT}/resultados.json`, JSON.stringify(res,null,1));
  await b.close();
  const fallas = res.filter(r => !r.ok).length;
  console.log(`${res.length - fallas} de ${res.length} casos pasan`);
  if (fallas) process.exitCode = 1;   // para que una automatización detecte las fallas
})().catch(e=>{ console.error('ERROR', e); require('fs').writeFileSync(`${OUT}/resultados.json`, JSON.stringify(res,null,1)); process.exit(1); });
