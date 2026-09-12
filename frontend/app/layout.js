import './globals.css';

export const metadata = {
  title: 'GrowUP | Decisiones que hacen crecer tu contenido',
  description: 'Consultoría de datos para creadores de contenido.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
