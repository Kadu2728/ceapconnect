"use client";

import { motion, useReducedMotion } from "framer-motion";

import { ProfileEditForm } from "@/features/profile/components/profile-edit-form";
import { ProfileHeader } from "@/features/profile/components/profile-header";
import { ProfileStats } from "@/features/profile/components/profile-stats";
import type { Profile } from "@/features/profile/types/profile.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface ProfileContentProps {
  data: Profile;
}

/**
 * Composição da Tela de Perfil: cabeçalho (quem é + nível) → estatísticas da
 * jornada → formulário de edição dos dados de contato.
 */
export function ProfileContent({ data }: ProfileContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="flex flex-col gap-6"
    >
      <motion.div variants={itemVariants}>
        <ProfileHeader profile={data} />
      </motion.div>
      <motion.div variants={itemVariants}>
        <ProfileStats stats={data.stats} />
      </motion.div>
      <motion.div variants={itemVariants}>
        <ProfileEditForm profile={data} />
      </motion.div>
    </motion.div>
  );
}
