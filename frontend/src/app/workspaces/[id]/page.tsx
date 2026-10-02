import { redirect } from 'next/navigation';

export default async function WorkspaceRoot({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const p = await params;
  redirect(`/workspaces/${p.id}/chat`);
}
