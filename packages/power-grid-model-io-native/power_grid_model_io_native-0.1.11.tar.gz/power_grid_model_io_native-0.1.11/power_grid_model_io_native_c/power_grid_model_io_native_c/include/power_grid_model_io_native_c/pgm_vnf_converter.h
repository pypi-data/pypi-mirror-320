// SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
//
// SPDX-License-Identifier: MPL-2.0

#pragma once
#ifndef POWER_GRID_MODEL_IO_NATIVE_C_PGM_VNF_CONVERTER_H
#define POWER_GRID_MODEL_IO_NATIVE_C_PGM_VNF_CONVERTER_H

#include "basics.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Create the PGM_IO_PgmVnfConverter
 * @param handle
 * @param file_buffer A pointer to the null-terminated C string.
 * @return The pointer to a PGM_IO_PgmVnfConverter instance. The instance must be freed by
 * PGM_IO_destroy_vnf_converter.
 */
PGM_IO_API PGM_IO_PgmVnfConverter* PGM_IO_create_pgm_vnf_converter(PGM_IO_Handle* handle, char const* file_buffer,
                                                                   PGM_IO_ExperimentalFeatures experimental_features);

/**
 * @brief Retrieve the transformed input data from .vnf format to PGM format.
 * @param handle
 * @param converter_ptr A pointer to a PGM_IO_PgmVnfConverter instace.
 * @return The pointer to the json string instance that holds data in PGM format.
 */
PGM_IO_API char const* PGM_IO_pgm_vnf_converter_get_input_data(PGM_IO_Handle* handle,
                                                               PGM_IO_PgmVnfConverter* converter_ptr);

/**
 * @brief Destroy the PGM_IO_PgmVnfConverter and free up the memory that was dedicated to it.
 * @param converter_ptr A pointer to a PGM_IO_PgmVnfConverter instance.
 */
PGM_IO_API void PGM_IO_destroy_pgm_vnf_converter(PGM_IO_PgmVnfConverter* converter_ptr);

#ifdef __cplusplus
}
#endif

#endif // POWER_GRID_MODEL_IO_NATIVE_C_PGM_VNF_CONVERTER_H
