import Footer from "../components/Footer";
import Cascate from "../components/Cascade";
import PlaceHolder from "../components/PlaceHolders";
import Menu from "../components/Menu";
import Head from "next/head";

import "bootstrap/dist/css/bootstrap.min.css";

import React from "react";
import { Container, Jumbotron } from "reactstrap";
import ThreeD from "../components/3D/ThreeDimensional";

export default function Home() {
  return (
    <div>
      <Head>
        <title>Tracker page</title>
        <meta
          name="description"
          content="Solar Tracker devoloped by JT iOsnaaente"
        />
        <meta name="author" content="iOsnaaente" />
      </Head>

      <header>
        <Menu />
      </header>

      <main className="flex">
        <section>
          <Jumbotron fluid className="servicos">
            <Container className="text-center">
              <div>
                <h1 className="display-4">Tracker JT</h1>
                <p className="lead">Inteligência em energia solar</p>
              </div>
            </Container>
          </Jumbotron>
        </section>

        <section className="mt-10 center">
          <PlaceHolder />
        </section>

        <section>
          <Cascate />
        </section>

        <section>
          <ThreeD />
        </section>
      </main>

      <footer>
        <Footer />
      </footer>

      <style>
        {` .servicos{
                    padding-top: 80px;
                    padding-bottom: 80px;
                    background-color: #070707; 
                    color: #f0f0f0;
                    margin-bottom: 0rem !important;
          }`}
      </style>
    </div>
  );
}
