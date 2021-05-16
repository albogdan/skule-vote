import React from "react";
// import Copyright from "../../General/Copyright/Copyright";
import { withStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import { ReactComponent as EngsocCrest } from "../images/EngsocCrest.svg";

const FooterPaper = withStyles({
  root: {
    //   minHeight: "100vh",
  },
})(Paper);

const Footer = ({ isLanding }) => {
  if (isLanding) {
    return (
      <FooterPaper>
        <EngsocCrest />
        <p>
          <b>University of Toronto Engineering Society</b>
        </p>
        <p>B740 Sandford Fleming Building</p>
        <p>10 King's College Road</p>
        <p>Toronto, Ontario, Canada M5S 3G4</p>
      </FooterPaper>
    );
  }
  // if (isLanding) {
  //     return {
  //         <FooterPaper>
  //             <p>Hi</p>
  //         </FooterPaper>
  //     }
  // } else {
  //     return
  // }
};

export default Footer;
