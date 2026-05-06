import { AuthTemplate } from "@/components/auth-template";

export default function SignUpPage(props: { searchParams?: { next?: string } }) {
  return <AuthTemplate mode="sign-up" nextPath={props.searchParams?.next} />;
}
