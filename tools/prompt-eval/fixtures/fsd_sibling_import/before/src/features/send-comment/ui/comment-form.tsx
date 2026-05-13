import { ActionButton } from './send-button';

interface Props {
  postId: string;
}

export function CommentForm({ postId }: Props) {
  function submit() {
    console.log('comment submitted for', postId);
  }
  return (
    <form>
      <textarea />
      <ActionButton onClick={submit}>Send</ActionButton>
    </form>
  );
}
