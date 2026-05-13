export function useLikePost(postId: string) {
  function like() {
    console.log('liked', postId);
  }
  return { like };
}
