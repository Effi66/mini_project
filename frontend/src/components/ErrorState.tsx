interface ErrorStateProps {
  message: string;
}

export function ErrorState({ message }: ErrorStateProps) {
  return (
    <section className="error-state" role="alert">
      <h2>生成失败</h2>
      <p>{message}</p>
    </section>
  );
}

