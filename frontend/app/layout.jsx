import './globals.css';

export const metadata = {
  title: 'CodeFlowAtlas',
  description: 'Understand source, runtime behavior, and engineering evidence.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
