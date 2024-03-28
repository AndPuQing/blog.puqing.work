import React, { useEffect, useMemo, useState } from "react";
import clsx from "clsx";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import styles from "./index.module.css";
import { inject } from "@vercel/analytics";
inject();

import * as config from "./_index.config";
import "react-responsive-carousel/lib/styles/carousel.min.css"; // requires a loader
import { useMediaQuery } from "react-responsive";
import "swiper/css";
import { useColorMode } from "@docusaurus/theme-common";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/zoom";
import SwiperCore, {
  Navigation,
  Pagination,
  Mousewheel,
  Keyboard,
  Zoom,
  EffectCreative,
} from "swiper";

SwiperCore.use([
  Zoom,
  Navigation,
  Pagination,
  Mousewheel,
  Keyboard,
  EffectCreative,
]);

function BlurBackgroundImage() {
  const isDarkTheme = useColorMode().colorMode === "dark";
  const anotherImgurl = isDarkTheme
    ? "/img/indexbackground_light.webp"
    : "/img/indexbackground_dark.webp";
  const imgurl = !isDarkTheme
    ? "/img/indexbackground_light.webp"
    : "/img/indexbackground_dark.webp";
  return (
    <div
      style={{
        backgroundImage: `url(${imgurl})`,
        backgroundAttachment: "fixed",
        backgroundSize: "cover",
        filter: `blur(10px) brightness(${isDarkTheme ? 0.7 : 1})`,
        transform: "scale(1.2)",
        position: "absolute",
        zIndex: 0,
        height: "100%",
        width: "100%",
      }}
    >
      <img src={anotherImgurl} alt="" style={{ display: "none" }} />
    </div>
  );
}

function HomepageBackground() {
  const { siteConfig } = useDocusaurusContext();
  const isDarkTheme = useColorMode().colorMode === "dark";
  return (
    <header
      className={clsx("hero themedHead", styles.heroBanner)}
      style={{
        minHeight: "calc(100vh - var(--ifm-navbar-height))",
        backgroundAttachment: "fixed",
        backgroundColor: isDarkTheme ? "#4E1F7A" : "#EB8B68",
      }}
    >
      <BrowserOnly>{BlurBackgroundImage}</BrowserOnly>
      <div className="container" style={{ zIndex: 1 }}>
        <div className="row">
          <div
            className={clsx(
              "col",
              "col--" + config.title_width,
              styles.centerChild
            )}
            style={{
              alignSelf: "center",
              marginBottom: "50px",
              minHeight: "30em",
            }}
          >
            <p
              className={`hero__title ${styles.focusin}`}
              style={{
                textShadow: `${isDarkTheme ? "#000000" : "#FFFFFF"}`,
              }}
            >
              {siteConfig.title}
            </p>
          </div>
          <div
            className={clsx(
              "col",
              "col--" + (12 - config.title_width),
              styles.centerChild
            )}
          >
            <BrowserOnly>{RandomImage}</BrowserOnly>
          </div>
        </div>
      </div>
    </header>
  );
}

function RandomImage() {
  const [loaded, setLoaded] = useState(false);
  const [imgsrc] = useState(
    () =>
      config.illustrations[
        Math.floor(Math.random() * config.illustrations.length)
      ]
  );
  const isMobile = useMediaQuery({ maxWidth: 1024 });
  return (
    <img
      src={imgsrc}
      className={clsx(styles.randomImage, loaded && styles.loaded)}
      style={{
        width: isMobile ? "70%" : "100%",
        alignSelf: "center",
      }}
      onLoad={() => {
        setLoaded(true);
      }}
    />
  );
}

function useHidingFooter() {
  useEffect(() => {
    const footer = document.querySelector(".footer") as HTMLElement;
    const docEle = document.documentElement;
    footer.style.transition = "opacity .3s";
    footer.style.opacity = "0";

    footer.style.display = "none";

    let shown = false;
    let wheelPaused = false;

    function pauseWheel() {
      wheelPaused = true;
      setTimeout(() => {
        wheelPaused = false;
      }, 500);
    }

    const onWheel = (e: WheelEvent) => {
      if (wheelPaused) {
        e.preventDefault();
        return;
      }
      if (
        !shown &&
        docEle.scrollTop > docEle.scrollHeight - window.innerHeight - 2 &&
        e.deltaY > 0
      ) {
        e.preventDefault();
        shown = true;
        footer.style.display = "";
        footer.style.opacity = "1";
        docEle.scrollTo({
          top: docEle.scrollHeight,
          behavior: "smooth",
        });
        pauseWheel();
      }
      if (shown && e.deltaY < 0) {
        e.preventDefault();
        shown = false;
        footer.style.opacity = "0";
        docEle.scrollTo({
          top: footer.offsetTop - window.innerHeight + 1,
          behavior: "smooth",
        });
        setTimeout(() => {
          footer.style.display = "none";
        }, 500);
        pauseWheel();
      }
    };

    window.addEventListener("mousewheel", onWheel, {
      passive: false,
      capture: true,
    });
    return () => {
      window.removeEventListener("mousewheel", onWheel, false);
    };
  }, []);
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  useHidingFooter();
  return (
    <Layout title={`${siteConfig.title}`}>
      <HomepageBackground />
    </Layout>
  );
}
