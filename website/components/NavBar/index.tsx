import s from "./navbar.module.css";

import { useState } from "react";
import cn from "classnames";
import Link from "next/link";
import { AiFillGithub } from "react-icons/ai";
import { Container } from "../Container";


const GitHubLink = () => (
  <a
    href="https://github.com/qnbhd/deployme"
    target="_blank"
    rel="noreferrer"
    className="hover:text-slate-300"
  >
    <AiFillGithub className="w-5 h-5" />
  </a>
);

export function NavBar() {
  const [mobileNavbar, setMobileNavbar] = useState(false);

  const toggleMobileNavbar = () => setMobileNavbar(!mobileNavbar);

  return (
    <div className={s.navbar}>
      <Container>
        <div className="flex justify-between py-6 m-auto">
          <div className="text-3xl font-bold">
            <Link href="/" passHref>
              <a>🚀 DeployMe</a>
            </Link>
          </div>

          <div className="flex items-center justify-end">
            <div className={s.desktopNavbar}>
            </div>

            <GitHubLink />

            <div className={s.mobileNavbar}>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileNavbar && (
          <div className="flex flex-col transition-all duration-300">
          </div>
        )}
      </Container>
    </div>
  );
}
