import React from "react";
import Image from "next/image";
import { Container, Row, Col, StyleSheet, Jumbotron } from "reactstrap";

const width = 250;
const height = 250;
const placeData = [
  {
    id: 1,
    title: "Dual Axis Tracking",
    imageSrc: "/images/Tracker.jpg",
    heading: "Tracker Dual Axis",
    content:
      "Tecnologia Tracker Single Axis com sistema de giro único, ideal para regiões de clima equatorial.",
    buttonText: "view details",
    buttonRef: "#",
  },
  {
    id: 2,
    title: "Rastreio inteligente",
    imageSrc: "/images/Smart.jpg",
    heading: "Rastreio inteligente",
    content:
      "Sistema com rastreio automático do sol, sendo capaz de rastrear em qualquer posição geográfica.",
    buttonText: "view details",
    buttonRef: "#",
  },
  {
    id: 3,
    title: "Tecnologia Ansys",
    imageSrc: "/images/Ansys_demo.png",
    heading: "Tecnologia Ansys",
    content:
      "Mais uma tecnologia Jet Towers desenvolvida pela nossa equipe de engenheiros qualificados.",
    buttonText: "view details",
    buttonRef: "#",
  },
];

const holders = placeData.map((item) => {
  return (
    <Col className="col-lg-4" key={item.id}>
      <div className="text-center mt-2rem mb-1rem">
        <Image
          priority
          className="bd-placeholder-img bd-placeholder-img-lg featurette-image img-fluid mx-auto"
          src={item.imageSrc}
          alt={item.title}
          width={width}
          height={height}
        />
      </div>
      <h2 className="text-center">{item.heading}</h2>
      <p className="text-center">{item.content}</p>
      <p className="text-center">
        <a className="btn btn-secondary" href={item.buttonRef}>
          {item.buttonText} &raquo;
        </a>
      </p>
      <style>
        {`
        .mt-2rem{
            margin-top: 1rem;
        }
        .mb-1rem{
            margin-bottom: 1rem;
        .mb-2rem{
            margin-bottom: 1rem;
        `}
      </style>
    </Col>
  );
});

export default function PlaceHolder() {
  return (
    <section className='mt-10 center'>
      <Jumbotron>
        <Container className="mt-10 container marketing">
          <hr className="featurette-divider" />
          <Row className="row center mt-10">{holders}</Row>
        </Container>
      </Jumbotron>
    </section>
  );
}
