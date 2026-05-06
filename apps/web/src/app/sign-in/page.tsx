import { AuthTemplate } from "@/components/auth-template";

export default function SignInPage(props: { searchParams?: { next?: string } }) {
  return <AuthTemplate mode="sign-in" nextPath={props.searchParams?.next} />;
}
