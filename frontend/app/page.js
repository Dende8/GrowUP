import InsightCard from '../components/InsightCard';

const services = [
  {
    number: '01',
    title: 'Lectura de canal',
    text: 'Ponemos orden a tus datos de YouTube Studio, TikTok Studio o Instagram para encontrar lo que de verdad está moviendo tu audiencia.',
  },
  {
    number: '02',
    title: 'Patrones que importan',
    text: 'Detectamos qué formatos, duraciones, ritmos y momentos de publicación están detrás de tus mejores resultados.',
  },
  {
    number: '03',
    title: 'Decisiones claras',
    text: 'Convertimos el análisis en recomendaciones concretas para que cada próximo contenido tenga una razón de ser.',
  },
];

const metrics = ['Contenido', 'Audiencia', 'Engagement', 'Crecimiento'];

export default function Home() {
  return (
    <main>
      <nav className="site-nav" aria-label="Navegación principal">
        <a className="brand" href="#inicio" aria-label="GrowUP, inicio">
          <span className="brand-mark">G</span>
          <span>GrowUP</span>
        </a>
        <div className="nav-links">
          <a href="#metodo">Método</a>
          <a href="#servicios">Qué hacemos</a>
          <a href="#contacto">Contacto</a>
        </div>
        <a className="nav-cta" href="mailto:contacto@growup.com">Hablemos <span aria-hidden="true">↗</span></a>
      </nav>

      <section className="hero" id="inicio">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-dot" /> Consultoría para creadores</p>
          <h1>Crece con<br /><em>intención.</em></h1>
          <p className="hero-intro">Tus plataformas ya tienen las respuestas. GrowUP las convierte en decisiones que hacen avanzar tu contenido.</p>
          <a className="button button-dark" href="#contacto">Descubre tu siguiente paso <span aria-hidden="true">↗</span></a>
        </div>
        <div className="hero-visual" aria-label="Resumen visual de crecimiento de audiencia">
          <div className="visual-topline"><span>SEÑAL DE CRECIMIENTO</span><span>+38.4%</span></div>
          <div className="chart-area">
            <div className="chart-label chart-label-top">alcance</div>
            <svg className="chart-line" viewBox="0 0 520 260" role="img" aria-label="Gráfico ascendente de rendimiento">
              <defs>
                <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0" stopColor="#c8ef49" stopOpacity=".38" />
                  <stop offset="1" stopColor="#c8ef49" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path className="chart-fill" d="M0 220 C50 205 55 175 95 190 S145 152 180 170 S220 122 260 140 S310 95 345 110 S390 76 425 90 S465 38 520 12 V260 H0Z" />
              <path className="chart-stroke" d="M0 220 C50 205 55 175 95 190 S145 152 180 170 S220 122 260 140 S310 95 345 110 S390 76 425 90 S465 38 520 12" />
              <circle className="chart-dot" cx="520" cy="12" r="6" />
            </svg>
            <div className="chart-axis"><span>ENE</span><span>FEB</span><span>MAR</span><span>ABR</span><span>MAY</span></div>
          </div>
          <div className="visual-bottomline"><span>EL DATO AISLADO NO BASTA.</span><strong>IMPORTA LA DIRECCIÓN.</strong></div>
        </div>
        <div className="hero-note">01 <span>Datos para dejar<br />de avanzar a ciegas</span></div>
      </section>

      <div className="ticker" aria-label="Áreas de análisis">
        {metrics.map((metric) => <span key={metric}>{metric} <b>✳</b></span>)}
      </div>

      <section className="manifesto section-wrap" id="metodo">
        <div className="section-kicker">/ La pregunta correcta</div>
        <div className="manifesto-content">
          <h2>¿Y si tu próximo salto<br />ya estuviera <em>en tus datos?</em></h2>
          <div className="manifesto-text">
            <p>Crear contenido no debería sentirse como lanzar monedas al aire. En un entorno donde cada publicación compite por un segundo de atención, entender qué funciona es una ventaja real.</p>
            <p>GrowUP analiza el comportamiento de tu canal para que puedas invertir tu tiempo en las ideas que tienen más posibilidades de crecer.</p>
            <a className="text-link" href="#servicios">Conoce nuestro método <span aria-hidden="true">→</span></a>
          </div>
        </div>
      </section>

      <section className="services section-wrap" id="servicios">
        <div className="section-heading">
          <div className="section-kicker">/ Lo que hacemos</div>
          <h2>De números<br />a <em>movimiento.</em></h2>
        </div>
        <div className="services-grid">
          {services.map((service) => <InsightCard key={service.number} number={service.number} title={service.title}>{service.text}</InsightCard>)}
        </div>
      </section>

      <section className="audience-section">
        <div className="audience-inner section-wrap">
          <div className="section-kicker">/ Para quién</div>
          <div className="audience-content">
            <h2>Para quien sabe<br />que puede <em>llegar más lejos.</em></h2>
            <p>Desde perfiles emergentes hasta cuentas consolidadas. Si quieres dejar de adivinar y empezar a entender, estás en el sitio correcto.</p>
            <div className="audience-tags"><span>Creadores emergentes</span><span>Canales consolidados</span><span>Equipos de contenido</span></div>
          </div>
        </div>
      </section>

      <section className="contact section-wrap" id="contacto">
        <div className="contact-kicker">/ Tu siguiente decisión</div>
        <h2>Hagamos que tus datos<br /><em>tengan algo que decir.</em></h2>
        <p>Cuéntanos dónde estás y vemos juntos hacia dónde puedes crecer.</p>
        <a className="button button-lime" href="mailto:contacto@growup.com?subject=Quiero%20hablar%20con%20GrowUP">contacto@growup.com <span aria-hidden="true">↗</span></a>
      </section>

      <footer className="site-footer">
        <a className="brand" href="#inicio"><span className="brand-mark">G</span><span>GrowUP</span></a>
        <span>Consultoría de datos para creadores</span>
        <span>© 2025 GrowUP</span>
      </footer>
    </main>
  );
}
