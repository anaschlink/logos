export function SkeletonList() {
  return (
    <div aria-busy="true" aria-label="Carregando incidentes">
      <p className="muted">
        Carregando… Se o serviço estava inativo, o primeiro acesso leva de 30 a 60 s (plano gratuito).
      </p>
      <div className="list">
        {Array.from({ length: 8 }, (_, i) => (
          <div key={i} className="skeleton" />
        ))}
      </div>
    </div>
  );
}