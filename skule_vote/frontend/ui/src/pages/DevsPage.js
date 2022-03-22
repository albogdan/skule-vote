import React from "react";
import { styled } from "@mui/system";
import photo2t2team from "images/2t2team.jpg";
import { Typography } from "@mui/material";
import { Spacer } from "assets/layout";

const ComicSans = styled(Typography)({
  fontFamily: "Comic Sans MS, Comic Sans, cursive",
  textAlign: "center",
});

const TeamImg = styled("img")({
  maxWidth: 900,
  width: "100%",
});

// Pls dont delete this :(
const DevsPage = () => (
  <>
    <Spacer y={24} />
    <TeamImg src={photo2t2team} alt="2T2 Team" />
    <Spacer y={24} />
    <ComicSans variant="h1" sx={{}}>
      Meet the Devs
    </ComicSans>
    <ComicSans
      variant="body2"
      sx={{ fontFamily: "Comic Sans MS, Comic Sans, cursive" }}
    >
      Lisa Alex Armin
    </ComicSans>
    <Spacer y={24} />
    <ComicSans variant="h2">
      Special thanks to the rest of the Skule Vote 2T2 Team
    </ComicSans>
    <ComicSans variant="body2">Zahir Jacquie Aidan Zach Ben</ComicSans>
    <Spacer y={24} />
    <ComicSans variant="h2">Shout out to the previous devs</ComicSans>
    <ComicSans variant="body2">Aleksei Jonathan Robert Michael Rafal</ComicSans>
  </>
);

export default DevsPage;
