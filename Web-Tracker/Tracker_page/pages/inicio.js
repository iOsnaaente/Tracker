import { Container, Jumbotron } from "reactstrap";

import Footer from "../components/primaryElements/Footer";
import MenuBar from "../components/primaryElements/MenuBar";

import axios from "axios";

const Index = ( dados ) => (
  <div>
    <h1> {dados} </h1>
  </div>
);

Index.getInitialProps = async () => {
  const response = await axios.get("http://localhost:1205/API");
  console.log(response);
  return { dados : response. }
};

export default function Inicio() {
  return (
    <div>
      <header>
        <MenuBar />
      </header>

      <main>
        <Jumbotron fluid className="servicos">
          <Container className="text-center">
            <h1 className="display-4">Tracker page</h1>
            <p className="lead">Página Inicial</p>
          </Container>
        </Jumbotron>

        <section>
          <div>
            <h1>Teste para aquisição de dados de uma API local</h1>
            <p id="p-inicio">Nada</p>
          </div>
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
