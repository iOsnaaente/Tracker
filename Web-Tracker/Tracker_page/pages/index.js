import getWindowSize from "../components/getWinSize";
import PlaceHolder from "../components/placeHolders";
import Cascate from "../components/Cascade";

import Footer from "../components/primaryElements/Footer";
import MenuBar from "../components/primaryElements/MenuBar";

import "bootstrap/dist/css/bootstrap.min.css";

import { Container, Jumbotron } from "reactstrap";

import React from "react";
import Head from "next/head";

export default function Home() {
  const size = getWindowSize();

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
        <MenuBar />
      </header>

      <main className="flex">
        <section>
          <Jumbotron fluid className="servicos">
            <Container className="text-center">
              <div>
                <h1 className="display-4">Tracker JT</h1>
                <p className="lead">
                  Uma tecnologia Jet Towers de inovações
                </p>
              </div>
            </Container>
          </Jumbotron>
        </section>

        <PlaceHolder />
        <Cascate />
      </main>

      <footer>
        <Footer />
      </footer>

      <style>
        {` .servicos{
                    padding-top: 110px;
                    padding-bottom: 60px;
                    background-color: #070707; 
                    color: #f0f0f0;
                    margin-bottom: 0rem !important;
          }`}
      </style>
    </div>
  );
}
