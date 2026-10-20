import Link from "next/link";

export default function Home() {
  return (
    <div className="card">
      <h1>HealthProfile</h1>
      <p>
        Demo HealthTech profile builder. All data is synthetic. This is not a
        medical product and gives no medical advice.
      </p>
      <div className="row">
        <Link href="/register">Create an account</Link>
        <Link href="/login">User login</Link>
        <Link href="/admin/login">Admin login</Link>
      </div>
    </div>
  );
}