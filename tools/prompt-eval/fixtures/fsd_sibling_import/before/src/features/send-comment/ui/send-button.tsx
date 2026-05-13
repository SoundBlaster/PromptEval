interface Props {
  onClick: () => void;
  children: React.ReactNode;
}

export function ActionButton({ onClick, children }: Props) {
  return <button onClick={onClick}>{children}</button>;
}
