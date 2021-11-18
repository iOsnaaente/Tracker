import { Container, Jumbotron } from "reactstrap";
import Image from "next/image";
import React from "react";
import { ImmediateRenderObject } from "three";

const itemsCascade = [
  {
    id: 1,
    title: "Sistema Tracker",
    titleSpan: " Dual Axis",
    paragraph:
      "Um seguidor solar ou tracker é um dispositivo que altera várias vezes a posição dos painéis fotovoltaicos durante o dia, \
      seguindo o caminho do sol para aumentar a produção de energia solar do sistema fotovoltaico. O uso de seguidores solares é \
      cada vez mais comum em usinas fotovoltaicas em outros países, uma vez que a indústria solar tem provado os grandes benefícios \
      que eles têm. Mas nem todo mundo entende os benefícios, vantagens e as desvantagens que um seguidor solar pode proporcionar \
      a um sistema fotovoltaico.",
    imageSource: "/images/Tracker.jpg",
    imageDescription: "/",
    width: 500,
    height: 500,
    classItem: "col-md-7",
  },
  {
    id: 2,
    title: "Descrição do ",
    titleSpan: "Tracker",
    paragraph:
      "Sistemas com seguidores solares geram mais energia do que os sistemas fixos. Isto ocorre devido ao aumento da exposição \
      direta aos raios solares, esse ganho pode alcançar valores de 25 a 45% (vide abaixo). De certa forma e com as devidas \
      características, faz sentido dizer que um sistema com seguidor solar que aumenta em 30% a produção de energia é semelhante \
      a um sistema fixo 30% maior (contém mais painéis fotovoltaicos).",
    imageSource: "/images/Ansys_demo.PNG",
    imageDescription: "/",
    width: 500,
    height: 500,
    classItem: "col-md-7 order-md-2",
  },
  {
    id: 3,
    title: "Parâmetros do",
    titleSpan: " Tracker",
    paragraph:
      "Seguidores solares geram mais eletricidade com aproximadamente a mesma quantidade de espaço necessário para os sistemas de \
      inclinação fixa, tornando-os ideais para otimizar o uso da área disponível. Outro aspecto muito importante a destacar é que, \
      graças ao rastreamento solar não só a produção de energia aumenta, mas também melhora a forma como a potência é entregue. \
      Vamos voltar para a imagem acima para entender esse conceito. Na curva em cinza vemos uma evolução da produção de energia \
      ao longo do dia, que aumenta gradualmente até chegando ao meio-dia, em seguida, retorna a diminuir. Mas, na curva verde, \
      vemos a forma como abordamos a potência máxima desde o início da manhã e que esta produção é mantida até o final da tarde. \
      Avanços na tecnologia e confiabilidade em eletrônica e mecânica reduziram drasticamente as preocupações de manutenção de \
      longo prazo para sistemas de rastreamento.",
    imageSource: "/images/Smart.jpg",
    imageDescription: "/",
    width: 500,
    height: 500,
    classItem: "col-md-7",
  },
];

const cascate = itemsCascade.map((item) => {
  return (
    <Jumbotron key={item.id}>
      <Container>
        <div>
          <div className="row featurette">
            <div className={item.classItem} >
              <h2 className="featurette-heading">
                {item.title}
                <span className="text-muted">{item.titleSpan}</span>
              </h2>
              <p className="lead">{item.paragraph}</p>
            </div>
            <div className="col-md-5 order-md-1">
              <Image
                priority
                src={item.imageSource}
                className="bd-placeholder-img bd-placeholder-img-lg featurette-image img-fluid mx-auto"
                height={item.height}
                width={item.width}
                alt={item.imageDescription}
              />
            </div>
          </div>
          <hr className="featurette-divider" />
        </div>
      </Container>
    </Jumbotron>
  );
});

export default function Cascate() {
  return (
    <section>
      <hr className="featurette-divider" />
      {cascate}
    </section>
  );
}
