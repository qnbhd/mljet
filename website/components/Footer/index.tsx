import { Container } from "../Container";

export function Footer() {
  return (
    <Container size="full" className="bg-violet-900">
      <Container className="py-10">
        <div className="text-center">
          Built for <a className="hover:text-chick" href="https://ai.itmo.ru/dataproducthack">Data Product Hack</a>
        </div>
      </Container>
    </Container>
  )
}